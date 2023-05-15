# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# pylint: disable=line-too-long, logging-fstring-interpolation, unused-argument

import os

from pathlib import Path
from re import match
from typing import Union

from azure.cli.core.azclierror import (ArgumentUsageError, CLIError, InvalidArgumentValueError,
                                       MutuallyExclusiveArgumentError, RequiredArgumentMissingError, ValidationError)
from azure.cli.core.commands.validators import validate_file_or_dict

from ._constants import EXT_REPO_NAME, EXT_REPO_OWNER
from ._data import Manifest
from ._github import get_github_latest_release_version, github_release_version_exists
from ._logging import get_logger
from ._utils import get_yaml_file_contents, get_yaml_file_path

log = get_logger(__name__)


def _get_arg_or_env(cmd, ns, arg_name: str, is_path: bool = False) -> Union[str, Path]:
    '''Get argument value from command line or environment variable.
    arg_name will be capitalized and prefixed with ADE_ to get the environment variable name.
    '''
    log.info(f"Validating argument: '{arg_name}'")
    env_var_name = f'ADE_{arg_name.upper()}'

    if hasattr(ns, arg_name):
        if (arg_value := getattr(ns, arg_name, None)):
            if is_path:
                arg_value = Path(arg_value).resolve()
            setattr(ns, arg_name, arg_value)
            return arg_value
        if (arg_value := os.environ.get(env_var_name, None)):
            if is_path:
                arg_value = Path(arg_value).resolve()
            setattr(ns, arg_name, arg_value)
            return arg_value
        cmd_arg_name = '/'.join(cmd.arguments[arg_name].type.settings['options_list'])
        raise RequiredArgumentMissingError(f"Missing required argument '{cmd_arg_name}'",
                                           recommendation=f"Please provide a value for '{cmd_arg_name}' "
                                           f"or set environment variable: '{env_var_name}'")
    raise CLIError(f'Invalid argument {arg_name}')


def catalog_validator(cmd, ns):
    catalog = _get_arg_or_env(cmd, ns, 'catalog', is_path=True)
    if not catalog.is_dir():
        raise InvalidArgumentValueError(f'Invalid catalog path: {catalog}')


def catalog_item_validator(cmd, ns):
    catalog_item = _get_arg_or_env(cmd, ns, 'catalog_item', is_path=True)
    if not catalog_item.is_dir():
        raise InvalidArgumentValueError(f'Invalid catalog item path: {catalog_item}')

    if hasattr(ns, 'manifest'):
        yaml_path = get_yaml_file_path(catalog_item, 'manifest', required=True)
        yaml_content = get_yaml_file_contents(yaml_path)
        ns.manifest = Manifest(yaml_content, yaml_path)


def action_name_validator(cmd, ns):
    _get_arg_or_env(cmd, ns, 'action_name')


def action_parameters_validator(cmd, ns):
    action_params = _get_arg_or_env(cmd, ns, 'action_parameters')
    ns.action_parameters = validate_file_or_dict(action_params)


def environment_resource_group_validator(cmd, ns):
    _get_arg_or_env(cmd, ns, 'environment_resource_group_name')


def ade_runner_run_command_validator(cmd, ns):
    catalog_validator(cmd, ns)
    catalog_item_validator(cmd, ns)

    runner: str = ns.manifest.runner
    template_path: Path = ns.manifest.template_path

    if runner:  # if runner is specified, validate template_path is the correct type for the runner
        if runner.lower() == 'arm' or runner.lower() == 'bicep':
            if template_path.suffix != '.json' and template_path.suffix != '.bicep':
                raise ArgumentUsageError(f'Invalid template file for {runner} runner: {template_path}',
                                         recommendation='Please provide a valid ARM/Bicep template '
                                         'file with .json or .bicep extension')
        elif runner.lower() == 'terraform' or runner.lower() == 'tf':
            if template_path.suffix != '.tf':
                raise ArgumentUsageError(f'Invalid template file for {runner} runner: {template_path}',
                                         recommendation='Please provide a valid Terraform template '
                                         'file with .tf extension')
        else:
            raise ArgumentUsageError(f'Invalid runner: {runner}',
                                     recommendation='Please provide a valid runner: ARM, Bicep, or Terraform')

    elif template_path:  # if template_path is specified, validate runner is the correct type for the template_path
        if template_path.suffix == '.tf' or str(template_path).lower().endswith('.tf.json'):
            runner = 'Terraform'
        elif template_path.suffix == '.bicep':
            runner = 'Bicep'
        elif template_path.suffix == '.json':
            runner = 'ARM'
        else:
            raise ArgumentUsageError(f'Invalid template file: {template_path}',
                                     recommendation='Please provide a valid ARM/Bicep/Terraform template '
                                     'file with .json/.bicep/.tf extension')

    # TODO: Add validation for other runners

    action_name_validator(cmd, ns)
    action_parameters_validator(cmd, ns)
    environment_resource_group_validator(cmd, ns)


def source_version_validator(cmd, ns):
    if ns.version:
        if ns.prerelease:
            raise MutuallyExclusiveArgumentError(
                'Only use one of --version/-v | --pre',
                recommendation='Remove all --version/-v, and --pre to use the latest stable release,'
                ' or only specify --pre to use the latest pre-release')

        _validate_version(cmd, ns)


def templates_version_validator(cmd, ns):
    if ns.local_templates:
        if sum(1 for ct in [ns.template_file, ns.version, ns.prerelease, ns.templates_url] if ct) > 1:
            raise MutuallyExclusiveArgumentError(
                '--local-template cannot be used with --templates-file | --templates-url | --version/-v | --pre',
                recommendation='Remove all templates-file, --templates-url, --version/-v, and --pre to use the latest'
                'stable release, or only specify --local to use templates packaged with the CLI')
    elif ns.template_file:
        if ns.version or ns.prerelease or ns.templates_url:
            raise MutuallyExclusiveArgumentError(
                '--template-file cannont be used with --templates-url | --version/-v | --pre',
                recommendation='Remove all --templates-url, --version/-v, and --pre to use a local template file.')
    else:
        if sum(1 for ct in [ns.version, ns.prerelease, ns.templates_url] if ct) > 1:
            raise MutuallyExclusiveArgumentError(
                'Only use one of --templates-url | --version/-v | --pre',
                recommendation='Remove all --templates-url, --version/-v, and --pre to use the latest'
                'stable release, or only specify --pre to use the latest pre-release')

        if ns.version:
            _validate_version(cmd, ns)

        elif ns.templates_url:
            if not _is_valid_url(ns.templates_url):
                raise InvalidArgumentValueError(
                    '--templates-url should be a valid url to a templates.json file')

        else:
            ns.version = ns.version or get_github_latest_release_version(prerelease=ns.prerelease)
            ns.templates_url = f'https://github.com/{EXT_REPO_OWNER}/{EXT_REPO_NAME}/releases/download/{ns.version}/templates.json'


def out_validator(cmd, ns):
    if hasattr(ns, 'outfile') and ns.outfile:
        if getattr(ns.outfile, 'is_default', None) is None:
            if ns.outdir or ns.stdout:
                raise MutuallyExclusiveArgumentError(
                    'Only use one of --outdir | --outfile | --stdout',
                    recommendation='Remove all --outdir, --outfile, and --stdout to output a bake.yaml file '
                    'in the current directory, or only specify --stdout to output to stdout.')
        ns.outfile = Path(ns.outfile).resolve()
    elif ns.outdir and ns.stdout:
        raise MutuallyExclusiveArgumentError(
            'Only use one of --outdir | --stdout',
            recommendation='Remove all --outdir and --stdout to output a bake.yaml file '
            'in the current directory, or only specify --stdout to output to stdout.')
    else:
        if hasattr(ns, 'outfile'):
            ns.outfile = None
        if ns.outdir:
            ns.outdir = _validate_dir_path(ns.outdir)


def _validate_dir_path(path: Union[str, Path], name: str = None):
    dir_path = (path if isinstance(path, Path) else Path(path)).resolve()
    not_exists = f'Could not find {name} directory at {dir_path}' if name else f'{dir_path} is not a file or directory'
    if not dir_path.exists():
        raise ValidationError(not_exists)
    if not dir_path.is_dir():
        raise ValidationError(f'{dir_path} is not a directory')
    return dir_path


def _validate_file_path(path: Union[str, Path], name: str = None):
    file_path = (path if isinstance(path, Path) else Path(path)).resolve()
    not_exists = f'Could not find {name} file at {file_path}' if name else f'{file_path} is not a file or directory'
    if not file_path.exists():
        raise ValidationError(not_exists)
    if not file_path.is_file():
        raise ValidationError(f'{file_path} is not a file')
    return file_path


def _validate_version(cmd, ns):
    ns.version = ns.version.lower()
    if ns.version[:1].isdigit():
        ns.version = 'v' + ns.version

    if not _is_valid_version(ns.version):
        raise InvalidArgumentValueError(
            '--version/-v should be in format v0.0.0 do not include -pre suffix')

    if not github_release_version_exists(version=ns.version):
        raise InvalidArgumentValueError(f'--version/-v {ns.version} does not exist')


def _is_valid_version(version: str):
    return match(r'^v[0-9]+\.[0-9]+\.[0-9]+$', version) is not None


def _is_valid_url(url: str):
    return match(
        r'^http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+$', url) is not None


def _none_or_empty(val):
    return val in ('', '""', "''") or val is None


# def user_validator(cmd, ns):
#     # Make sure these arguments are non-empty strings.
#     # When they are accidentally provided as an empty string "", they won't take effect when filtering the role
#     # assignments, causing all matched role assignments to be listed/deleted. For example,
#     #   az role assignment delete --assignee ""
#     # removes all role assignments under the subscription.
#     if getattr(ns, 'user_id') == "":
#         # Get option name, like user_id -> --user-id
#         option_name = cmd.arguments['user_id'].type.settings['options_list'][0]
#         raise RequiredArgumentMissingError(f'usage error: {option_name} can\'t be an empty string.')
