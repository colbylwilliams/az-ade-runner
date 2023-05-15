# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# pylint: disable=logging-fstring-interpolation

import json
import shutil
import subprocess
import sys

from pathlib import Path

from azure.cli.core.azclierror import ValidationError

from ._constants import IN_RUNNER
from ._logging import get_logger

log = get_logger(__name__)


def check_terraform_install(raise_error=True):
    '''Checks if terraform is installed'''
    log.info('Checking if terraform is installed')
    terraform = shutil.which('terraform')
    installed = bool(terraform)
    if not installed and raise_error:
        raise ValidationError('Terraform is not installed. Please install terraform and try again.')
    return installed


def _parse_command(command):
    '''Parses a command (string or list of args), adds required arguments, and replaces executable with full path'''
    if isinstance(command, list):
        args = command
    elif isinstance(command, str):
        args = command.split()
    else:
        raise ValueError(f'command must be a string or list, not {type(command)}')

    # get full path to terraform executable
    terraform = shutil.which('terraform')

    # remove 'tf' or 'terraform' from the beginning args
    if args[0] == 'tf' or args[0] == 'terraform':
        args.pop(0)

    # ensure the full path to the terraform executable is the first arg
    if args[0] != terraform:
        args = [terraform] + args

    # convert all Path objects to strings
    for i, arg in enumerate(args):
        if isinstance(arg, Path):
            args[i] = str(arg)

    # ensure all args are strings
    for i, arg in enumerate(args):
        if not isinstance(arg, str):
            raise ValueError(f'arg {i} in {str(command)} is must be a string: {arg} ({type(arg)})')

    # add -no-color if running in a the runner container
    if IN_RUNNER and '-no-color' not in args:
        if len(args) > 2:
            args.insert(2, '-no-color')
        else:
            args.append('-no-color')

    return args


def _execute_terraform(command):
    '''Runs a terraform command'''
    args = _parse_command(command)
    log.info(f'Executing terraform {args[1]}')
    log.info(f'Running terraform command: {" ".join(args)}')
    proc = subprocess.run(args, stdout=sys.stdout, stderr=sys.stderr, check=True, text=True)
    log.info(f'Done executing terraform {args[1]}')
    return proc.returncode


def terraform_init():
    '''Executes the terraform init command'''
    command = ['init']
    return _execute_terraform(command)


def terraform_plan(state_file: Path, plan_file: Path, vars_file: Path,
                   resource_group_name: str, destroy: bool = False):
    '''Executes the terraform plan command'''
    command = [
        'plan',
        '-compact-warnings',
        '-refresh=true',
        '-lock=true',
        f'-state={state_file}',
        f'-out={plan_file}',
        f'-var-file="{vars_file}"',
        f'-var "resource_group_name={resource_group_name}"'
    ]

    if destroy:
        command.insert(3, '-destroy')

    return _execute_terraform(command)


def terraform_apply(state_file: Path, plan_file: Path):
    '''Executes the terraform apply command'''
    command = [
        'apply',
        '-compact-warnings',
        '-auto-approve',
        '-lock=true',
        f'-state={state_file}',
        plan_file
    ]
    return _execute_terraform(command)


def execute_terraform(storage_dir: Path, temp_dir: Path, parameters: dict, resource_group_name: str, destroy: bool = False):
    '''Executes the terraform init, plan, and apply commands'''

    state_file = storage_dir / 'environment.tfstate'
    plan_file = temp_dir / 'environment.tfplan'
    vars_file = temp_dir / 'environment.tfvars.json'

    # write the environment variables to a file
    with open(vars_file, 'w') as f:
        json.dump(parameters, f, ensure_ascii=False, indent=4, sort_keys=True)

    if (exit_code := terraform_init()) != 0:
        raise ValidationError(f'Terraform init failed with exit code {exit_code}')

    if (exit_code := terraform_plan(state_file, plan_file, vars_file, resource_group_name, destroy)) != 0:
        raise ValidationError(f'Terraform plan failed with exit code {exit_code}')

    if (exit_code := terraform_apply(state_file, plan_file)) != 0:
        raise ValidationError(f'Terraform apply failed with exit code {exit_code}')

    return exit_code
