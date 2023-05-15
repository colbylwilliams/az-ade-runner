# ------------------------------------
# Copyright (c) Microsoft Corporation.
# Licensed under the MIT License.
# ------------------------------------
# pylint: disable=line-too-long

import os

from datetime import datetime, timezone
from pathlib import Path

timestamp = datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S')

EXT_NAME = 'ade-runner'
EXT_NAME_CLEAN = EXT_NAME.replace('-', '_')
EXT_DESCRIPTION = 'ADE Runner'

EXT_DIR_NAME = f'azext_{EXT_NAME_CLEAN}'
EXT_REPO_NAME = f'az-{EXT_NAME}'
EXT_REPO_OWNER = 'colbylwilliams'

ADE_RUNNER = 'ADE_RUNNER'

IN_RUNNER = os.environ.get(ADE_RUNNER)
IN_RUNNER = bool(IN_RUNNER)

# The Azure Region to deploy the Environment's resources.
ADE_ENVIRONMENT_LOCATION = 'ADE_ENVIRONMENT_LOCATION'
# The resource id for subscription that the Environment's resource group is in.
# For example: /subscriptions/159f2485-xxxx-xxxx-xxxx-xxxxxxxxxxxx.
ADE_ENVIRONMENT_SUBSCRIPTION = 'ADE_ENVIRONMENT_SUBSCRIPTION'
# The unique id(guid) for subscription that the Environment's resource group is in.
# This will have the same value as ARM_SUBSCRIPTION_ID.
ADE_ENVIRONMENT_SUBSCRIPTION_ID = 'ADE_ENVIRONMENT_SUBSCRIPTION_ID'
# The id of the Environment's resource group.
# For example: /subscriptions/159f2485-xxxx-xxxx-xxxx-xxxxxxxxxxxx/resourceGroups/ADE_ENVIRONMENT_RESOURCE_GROUP_NAME.
ADE_ENVIRONMENT_RESOURCE_GROUP_ID = 'ADE_ENVIRONMENT_RESOURCE_GROUP_ID'
# The name of the Environment's resource group. This will have the same value as ARM_RESOURCE_GROUP_NAME.
ADE_ENVIRONMENT_RESOURCE_GROUP_NAME = 'ADE_ENVIRONMENT_RESOURCE_GROUP_NAME'
# Always set to /mnt/storage/.artifacts. The path to a persistent(file share) directory.
# This directory will be persisted between actions. Files saved to this directory will be available via the Dataplane.
ADE_ENVIRONMENT_ARTIFACTS = 'ADE_ENVIRONMENT_ARTIFACTS'

# The unique id(guid) of the action.
ADE_ACTION_ID = 'ADE_ACTION_ID'
# The name of the action to execute. For example: deploy.
ADE_ACTION_NAME = 'ADE_ACTION_NAME'
# A JSON object with the input parameters for the action.
ADE_ACTION_PARAMETERS = 'ADE_ACTION_PARAMETERS'
# Always set to /mnt/storage. The path to a persistent(file share) directory.
# This directory will be persisted between actions.
ADE_ACTION_STORAGE = 'ADE_ACTION_STORAGE'
# Always set to /mnt/temporary. The path to a temporary directory. This directory will not be persisted between actions.
ADE_ACTION_TEMP = 'ADE_ACTION_TEMP'
# Always set to /mnt/storage/.output/$ACTION_ID
ADE_ACTION_OUTPUT = 'ADE_ACTION_OUTPUT'

# The path to the Catalog within the cloned Catalog git repository. For example: /mnt/catalog/root/Catalog
ADE_CATALOG = 'ADE_CATALOG'
# The name of the Catalog
ADE_CATALOG_NAME = 'ADE_CATALOG_NAME'
# The path to CatalogItem folder within the cloned Catalog git repository.
# For example: /mnt/catalog/root/Catalog/FunctionApp
ADE_CATALOG_ITEM = 'ADE_CATALOG_ITEM'
# The name of the Catalog Item
ADE_CATALOG_ITEM_NAME = 'ADE_CATALOG_ITEM_NAME'
# The path to CatalogItem template file within the cloned Catalog git repository.
# For example: /mnt/catalog/root/Catalog/FunctionApp/azuredeploy.json
ADE_CATALOG_ITEM_TEMPLATE = 'ADE_CATALOG_ITEM_TEMPLATE'

_temp = os.environ.get(ADE_ACTION_TEMP)
_storage = os.environ.get(ADE_ACTION_STORAGE)
_output = os.environ.get(ADE_ACTION_OUTPUT)

ACTION_ID = os.environ.get(ADE_ACTION_ID)
ACTION_NAME = os.environ.get(ADE_ACTION_NAME)
CATALOG = os.environ.get(ADE_CATALOG)
CATALOG_ITEM = os.environ.get(ADE_CATALOG_ITEM)

ENVIRONMENT_RESOURCE_GROUP_NAME = os.environ.get(ADE_ENVIRONMENT_RESOURCE_GROUP_NAME)

TEMP_DIR = Path(_temp).resolve() if IN_RUNNER \
    else Path(__file__).resolve().parent.parent.parent / '.local' / 'temp'

STORAGE_DIR = Path(_storage).resolve() if IN_RUNNER \
    else Path(__file__).resolve().parent.parent.parent / '.local' / 'storage'

OUTPUT_DIR = Path(_output).resolve() if IN_RUNNER \
    else Path(__file__).resolve().parent.parent.parent / '.local' / 'storage' / '.output' / 'action'

CATALOG_ITEM_DIR = Path(CATALOG_ITEM).resolve() if IN_RUNNER \
    else Path(__file__).resolve().parent.parent.parent / '.local' / 'Environments' / 'Echo'

# if IN_RUNNER:
#     STORAGE_DIR.mkdir(parents=True, exist_ok=True)
