# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------

from azure.cli.core.commands.client_factory import get_mgmt_service_client
from azure.cli.core.profiles import ResourceType


def cf_resources(cli_ctx, **_):
    from azure.mgmt.resource.resources import ResourceManagementClient
    client: ResourceManagementClient = get_mgmt_service_client(cli_ctx, ResourceType.MGMT_RESOURCE_RESOURCES)
    return client


def cf_storage(cli_ctx, **_):
    from azure.mgmt.storage import StorageManagementClient
    client: StorageManagementClient = get_mgmt_service_client(cli_ctx, ResourceType.MGMT_STORAGE)
    return client


def cf_network(cli_ctx, **_):
    from azure.mgmt.network import NetworkManagementClient
    client: NetworkManagementClient = get_mgmt_service_client(cli_ctx, ResourceType.MGMT_NETWORK)
    return client


def cf_keyvault(cli_ctx, **_):
    from azure.mgmt.keyvault import KeyVaultManagementClient
    client: KeyVaultManagementClient = get_mgmt_service_client(cli_ctx, ResourceType.MGMT_KEYVAULT)
    return client


def cf_auth(cli_ctx, scope=None):
    import re
    subscription_id = None
    if scope:
        matched = re.match('/subscriptions/(?P<subscription>[^/]*)/', scope)
        if matched:
            subscription_id = matched.groupdict()['subscription']
    return get_mgmt_service_client(cli_ctx, ResourceType.MGMT_AUTHORIZATION, subscription_id=subscription_id)


def get_graph_client(cli_ctx):
    # https://github.com/Azure/azure-cli/blob/dev/doc/microsoft_graph_client.md
    from azure.cli.command_modules.role import graph_client_factory
    return graph_client_factory(cli_ctx)


def cf_compute(cli_ctx, **kwargs):
    from azure.mgmt.compute import ComputeManagementClient
    client: ComputeManagementClient = get_mgmt_service_client(cli_ctx, ResourceType.MGMT_COMPUTE,
                                                              subscription_id=kwargs.get('subscription_id'),
                                                              aux_subscriptions=kwargs.get('aux_subscriptions'))
    return client


def cf_galleries(cli_ctx, _):
    return cf_compute(cli_ctx).galleries


def cf_gallery_images(cli_ctx, _):
    return cf_compute(cli_ctx).gallery_images


def cf_gallery_image_versions(cli_ctx, _):
    return cf_compute(cli_ctx).gallery_image_versions


def cf_gallery_application(cli_ctx, *_):
    return cf_compute(cli_ctx).gallery_applications


def cf_gallery_application_version(cli_ctx, *_):
    return cf_compute(cli_ctx).gallery_application_versions


def cf_msi(cli_ctx, **_):
    from azure.mgmt.msi import ManagedServiceIdentityClient
    client: ManagedServiceIdentityClient = get_mgmt_service_client(cli_ctx, ResourceType.MGMT_MSI)
    return client


def cf_user_identities(cli_ctx, _):
    return cf_msi(cli_ctx).user_assigned_identities


# def cf_container(cli_ctx, *_):
#     from azure.mgmt.containerinstance import ContainerInstanceManagementClient
#     return get_mgmt_service_client(cli_ctx, ContainerInstanceManagementClient).containers


# def cf_container_groups(cli_ctx, *_):
#     from azure.mgmt.containerinstance import ContainerInstanceManagementClient
#     return get_mgmt_service_client(cli_ctx, ContainerInstanceManagementClient).container_groups


# def _msi_operations_operations(cli_ctx, _):
#     return cf_msi(cli_ctx).operations


# def _msi_federated_identity_credentials_operations(cli_ctx, _):
#     return cf_msi(cli_ctx).federated_identity_credentials
