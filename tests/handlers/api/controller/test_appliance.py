#!/usr/bin/env python
#
# Copyright (C) 2016 GNS3 Technologies Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import uuid
import pytest
from unittest.mock import MagicMock
from tests.utils import asyncio_patch


from gns3server.controller import Controller
from gns3server.controller.appliance import Appliance


@pytest.fixture
def compute(http_controller, async_run):
    compute = MagicMock()
    compute.id = "example.com"
    compute.host = "example.org"
    Controller.instance()._computes = {"example.com": compute}
    return compute


@pytest.fixture
def project(http_controller, async_run):
    return async_run(Controller.instance().add_project(name="Test"))


def test_appliance_list(http_controller, controller):

    id = str(uuid.uuid4())
    controller.load_appliances()
    controller._appliances[id] = Appliance(id, {
        "appliance_type": "qemu",
        "category": 0,
        "name": "test",
        "symbol": "guest.svg",
        "default_name_format": "{name}-{0}",
        "compute_id": "local"
    })
    response = http_controller.get("/appliances", example=True)
    assert response.status == 200
    assert response.route == "/appliances"
    assert len(response.json) > 0


def test_appliance_templates_list(http_controller, controller, async_run):

    controller.load_appliance_templates()
    response = http_controller.get("/appliances/templates", example=True)
    assert response.status == 200
    assert len(response.json) > 0


def test_cr(http_controller, controller, async_run):

    controller.load_appliance_templates()
    response = http_controller.get("/appliances/templates", example=True)
    assert response.status == 200
    assert len(response.json) > 0


def test_appliance_create_without_id(http_controller, controller):

    params = {"base_script_file": "vpcs_base_config.txt",
              "category": "guest",
              "console_auto_start": False,
              "console_type": "telnet",
              "default_name_format": "PC{0}",
              "name": "VPCS_TEST",
              "compute_id": "local",
              "symbol": ":/symbols/vpcs_guest.svg",
              "appliance_type": "vpcs"}

    response = http_controller.post("/appliances", params, example=True)
    assert response.status == 201
    assert response.route == "/appliances"
    assert response.json["appliance_id"] is not None
    assert len(controller.appliances) == 1


def test_appliance_create_with_id(http_controller, controller):

    params = {"appliance_id": str(uuid.uuid4()),
              "base_script_file": "vpcs_base_config.txt",
              "category": "guest",
              "console_auto_start": False,
              "console_type": "telnet",
              "default_name_format": "PC{0}",
              "name": "VPCS_TEST",
              "compute_id": "local",
              "symbol": ":/symbols/vpcs_guest.svg",
              "appliance_type": "vpcs"}

    response = http_controller.post("/appliances", params, example=True)
    assert response.status == 201
    assert response.route == "/appliances"
    assert response.json["appliance_id"] is not None
    assert len(controller.appliances) == 1


def test_appliance_create_wrong_type(http_controller, controller):

    params = {"appliance_id": str(uuid.uuid4()),
              "base_script_file": "vpcs_base_config.txt",
              "category": "guest",
              "console_auto_start": False,
              "console_type": "telnet",
              "default_name_format": "PC{0}",
              "name": "VPCS_TEST",
              "compute_id": "local",
              "symbol": ":/symbols/vpcs_guest.svg",
              "appliance_type": "invalid_appliance_type"}

    response = http_controller.post("/appliances", params)
    assert response.status == 400
    assert len(controller.appliances) == 0


def test_appliance_get(http_controller, controller):

    appliance_id = str(uuid.uuid4())
    params = {"appliance_id": appliance_id,
              "base_script_file": "vpcs_base_config.txt",
              "category": "guest",
              "console_auto_start": False,
              "console_type": "telnet",
              "default_name_format": "PC{0}",
              "name": "VPCS_TEST",
              "compute_id": "local",
              "symbol": ":/symbols/vpcs_guest.svg",
              "appliance_type": "vpcs"}

    response = http_controller.post("/appliances", params)
    assert response.status == 201

    response = http_controller.get("/appliances/{}".format(appliance_id), example=True)
    assert response.status == 200
    assert response.json["appliance_id"] == appliance_id


def test_appliance_update(http_controller, controller):

    appliance_id = str(uuid.uuid4())
    params = {"appliance_id": appliance_id,
              "base_script_file": "vpcs_base_config.txt",
              "category": "guest",
              "console_auto_start": False,
              "console_type": "telnet",
              "default_name_format": "PC{0}",
              "name": "VPCS_TEST",
              "compute_id": "local",
              "symbol": ":/symbols/vpcs_guest.svg",
              "appliance_type": "vpcs"}

    response = http_controller.post("/appliances", params)
    assert response.status == 201

    response = http_controller.get("/appliances/{}".format(appliance_id))
    assert response.status == 200
    assert response.json["appliance_id"] == appliance_id

    params["name"] = "VPCS_TEST_RENAMED"
    response = http_controller.put("/appliances/{}".format(appliance_id), params, example=True)

    assert response.status == 200
    assert response.json["name"] == "VPCS_TEST_RENAMED"


def test_appliance_delete(http_controller, controller):

    appliance_id = str(uuid.uuid4())
    params = {"appliance_id": appliance_id,
              "base_script_file": "vpcs_base_config.txt",
              "category": "guest",
              "console_auto_start": False,
              "console_type": "telnet",
              "default_name_format": "PC{0}",
              "name": "VPCS_TEST",
              "compute_id": "local",
              "symbol": ":/symbols/vpcs_guest.svg",
              "appliance_type": "vpcs"}

    response = http_controller.post("/appliances", params)
    assert response.status == 201

    response = http_controller.get("/appliances")
    assert len(response.json) == 1
    assert len(controller.appliances) == 1

    response = http_controller.delete("/appliances/{}".format(appliance_id), example=True)
    assert response.status == 204

    response = http_controller.get("/appliances")
    assert len(response.json) == 0
    assert len(controller.appliances) == 0


def test_c7200_dynamips_appliance_create(http_controller):

    params = {"name": "Cisco c7200 appliance",
              "platform": "c7200",
              "compute_id": "local",
              "image": "c7200-adventerprisek9-mz.124-24.T5.image",
              "appliance_type": "dynamips"}

    response = http_controller.post("/appliances", params, example=True)
    assert response.status == 201
    assert response.json["appliance_id"] is not None

    expected_response = {"appliance_type": "dynamips",
                         "auto_delete_disks": False,
                         "builtin": False,
                         "category": "router",
                         "compute_id": "local",
                         "console_auto_start": False,
                         "console_type": "telnet",
                         "default_name_format": "R{0}",
                         "disk0": 0,
                         "disk1": 0,
                         "exec_area": 64,
                         "idlemax": 500,
                         "idlepc": "",
                         "idlesleep": 30,
                         "image": "c7200-adventerprisek9-mz.124-24.T5.image",
                         "mac_addr": "",
                         "midplane": "vxr",
                         "mmap": True,
                         "name": "Cisco c7200 appliance",
                         "npe": "npe-400",
                         "nvram": 512,
                         "platform": "c7200",
                         "private_config": "",
                         "ram": 512,
                         "sparsemem": True,
                         "startup_config": "ios_base_startup-config.txt",
                         "symbol": ":/symbols/router.svg",
                         "system_id": "FTX0945W0MY"}

    for item, value in expected_response.items():
        assert response.json.get(item) == value


def test_c3745_dynamips_appliance_create(http_controller):

    params = {"name": "Cisco c3745 appliance",
              "platform": "c3745",
              "compute_id": "local",
              "image": "c3745-adventerprisek9-mz.124-25d.image",
              "appliance_type": "dynamips"}

    response = http_controller.post("/appliances", params, example=True)
    assert response.status == 201
    assert response.json["appliance_id"] is not None

    expected_response = {"appliance_type": "dynamips",
                         "auto_delete_disks": False,
                         "builtin": False,
                         "category": "router",
                         "compute_id": "local",
                         "console_auto_start": False,
                         "console_type": "telnet",
                         "default_name_format": "R{0}",
                         "disk0": 0,
                         "disk1": 0,
                         "exec_area": 64,
                         "idlemax": 500,
                         "idlepc": "",
                         "idlesleep": 30,
                         "image": "c3745-adventerprisek9-mz.124-25d.image",
                         "mac_addr": "",
                         "mmap": True,
                         "name": "Cisco c3745 appliance",
                         "iomem": 5,
                         "nvram": 256,
                         "platform": "c3745",
                         "private_config": "",
                         "ram": 256,
                         "sparsemem": True,
                         "startup_config": "ios_base_startup-config.txt",
                         "symbol": ":/symbols/router.svg",
                         "system_id": "FTX0945W0MY"}

    for item, value in expected_response.items():
        assert response.json.get(item) == value


def test_c3725_dynamips_appliance_create(http_controller):

    params = {"name": "Cisco c3725 appliance",
              "platform": "c3725",
              "compute_id": "local",
              "image": "c3725-adventerprisek9-mz.124-25d.image",
              "appliance_type": "dynamips"}

    response = http_controller.post("/appliances", params)
    assert response.status == 201
    assert response.json["appliance_id"] is not None

    expected_response = {"appliance_type": "dynamips",
                         "auto_delete_disks": False,
                         "builtin": False,
                         "category": "router",
                         "compute_id": "local",
                         "console_auto_start": False,
                         "console_type": "telnet",
                         "default_name_format": "R{0}",
                         "disk0": 0,
                         "disk1": 0,
                         "exec_area": 64,
                         "idlemax": 500,
                         "idlepc": "",
                         "idlesleep": 30,
                         "image": "c3725-adventerprisek9-mz.124-25d.image",
                         "mac_addr": "",
                         "mmap": True,
                         "name": "Cisco c3725 appliance",
                         "iomem": 5,
                         "nvram": 256,
                         "platform": "c3725",
                         "private_config": "",
                         "ram": 128,
                         "sparsemem": True,
                         "startup_config": "ios_base_startup-config.txt",
                         "symbol": ":/symbols/router.svg",
                         "system_id": "FTX0945W0MY"}

    for item, value in expected_response.items():
        assert response.json.get(item) == value


def test_c3600_dynamips_appliance_create(http_controller):

    params = {"name": "Cisco c3600 appliance",
              "platform": "c3600",
              "chassis": "3660",
              "compute_id": "local",
              "image": "c3660-a3jk9s-mz.124-25d.image",
              "appliance_type": "dynamips"}

    response = http_controller.post("/appliances", params, example=True)
    assert response.status == 201
    assert response.json["appliance_id"] is not None

    expected_response = {"appliance_type": "dynamips",
                         "auto_delete_disks": False,
                         "builtin": False,
                         "category": "router",
                         "compute_id": "local",
                         "console_auto_start": False,
                         "console_type": "telnet",
                         "default_name_format": "R{0}",
                         "disk0": 0,
                         "disk1": 0,
                         "exec_area": 64,
                         "idlemax": 500,
                         "idlepc": "",
                         "idlesleep": 30,
                         "image": "c3660-a3jk9s-mz.124-25d.image",
                         "mac_addr": "",
                         "mmap": True,
                         "name": "Cisco c3600 appliance",
                         "iomem": 5,
                         "nvram": 128,
                         "platform": "c3600",
                         "chassis": "3660",
                         "private_config": "",
                         "ram": 192,
                         "sparsemem": True,
                         "startup_config": "ios_base_startup-config.txt",
                         "symbol": ":/symbols/router.svg",
                         "system_id": "FTX0945W0MY"}

    for item, value in expected_response.items():
        assert response.json.get(item) == value


def test_c3600_dynamips_appliance_create_wrong_chassis(http_controller):

    params = {"name": "Cisco c3600 appliance",
              "platform": "c3600",
              "chassis": "3650",
              "compute_id": "local",
              "image": "c3660-a3jk9s-mz.124-25d.image",
              "appliance_type": "dynamips"}

    response = http_controller.post("/appliances", params)
    assert response.status == 400


def test_c2691_dynamips_appliance_create(http_controller):

    params = {"name": "Cisco c2691 appliance",
              "platform": "c2691",
              "compute_id": "local",
              "image": "c2691-adventerprisek9-mz.124-25d.image",
              "appliance_type": "dynamips"}

    response = http_controller.post("/appliances", params)
    assert response.status == 201
    assert response.json["appliance_id"] is not None

    expected_response = {"appliance_type": "dynamips",
                         "auto_delete_disks": False,
                         "builtin": False,
                         "category": "router",
                         "compute_id": "local",
                         "console_auto_start": False,
                         "console_type": "telnet",
                         "default_name_format": "R{0}",
                         "disk0": 0,
                         "disk1": 0,
                         "exec_area": 64,
                         "idlemax": 500,
                         "idlepc": "",
                         "idlesleep": 30,
                         "image": "c2691-adventerprisek9-mz.124-25d.image",
                         "mac_addr": "",
                         "mmap": True,
                         "name": "Cisco c2691 appliance",
                         "iomem": 5,
                         "nvram": 256,
                         "platform": "c2691",
                         "private_config": "",
                         "ram": 192,
                         "sparsemem": True,
                         "startup_config": "ios_base_startup-config.txt",
                         "symbol": ":/symbols/router.svg",
                         "system_id": "FTX0945W0MY"}

    for item, value in expected_response.items():
        assert response.json.get(item) == value


def test_c2600_dynamips_appliance_create(http_controller):

    params = {"name": "Cisco c2600 appliance",
              "platform": "c2600",
              "chassis": "2651XM",
              "compute_id": "local",
              "image": "c2600-adventerprisek9-mz.124-25d.image",
              "appliance_type": "dynamips"}

    response = http_controller.post("/appliances", params, example=True)
    assert response.status == 201
    assert response.json["appliance_id"] is not None

    expected_response = {"appliance_type": "dynamips",
                         "auto_delete_disks": False,
                         "builtin": False,
                         "category": "router",
                         "compute_id": "local",
                         "console_auto_start": False,
                         "console_type": "telnet",
                         "default_name_format": "R{0}",
                         "disk0": 0,
                         "disk1": 0,
                         "exec_area": 64,
                         "idlemax": 500,
                         "idlepc": "",
                         "idlesleep": 30,
                         "image": "c2600-adventerprisek9-mz.124-25d.image",
                         "mac_addr": "",
                         "mmap": True,
                         "name": "Cisco c2600 appliance",
                         "iomem": 15,
                         "nvram": 128,
                         "platform": "c2600",
                         "chassis": "2651XM",
                         "private_config": "",
                         "ram": 160,
                         "sparsemem": True,
                         "startup_config": "ios_base_startup-config.txt",
                         "symbol": ":/symbols/router.svg",
                         "system_id": "FTX0945W0MY"}

    for item, value in expected_response.items():
        assert response.json.get(item) == value


def test_c2600_dynamips_appliance_create_wrong_chassis(http_controller):

    params = {"name": "Cisco c2600 appliance",
              "platform": "c2600",
              "chassis": "2660XM",
              "compute_id": "local",
              "image": "c2600-adventerprisek9-mz.124-25d.image",
              "appliance_type": "dynamips"}

    response = http_controller.post("/appliances", params)
    assert response.status == 400


def test_c1700_dynamips_appliance_create(http_controller):

    params = {"name": "Cisco c1700 appliance",
              "platform": "c1700",
              "chassis": "1760",
              "compute_id": "local",
              "image": "c1700-adventerprisek9-mz.124-25d.image",
              "appliance_type": "dynamips"}

    response = http_controller.post("/appliances", params, example=True)
    assert response.status == 201
    assert response.json["appliance_id"] is not None

    expected_response = {"appliance_type": "dynamips",
                         "auto_delete_disks": False,
                         "builtin": False,
                         "category": "router",
                         "compute_id": "local",
                         "console_auto_start": False,
                         "console_type": "telnet",
                         "default_name_format": "R{0}",
                         "disk0": 0,
                         "disk1": 0,
                         "exec_area": 64,
                         "idlemax": 500,
                         "idlepc": "",
                         "idlesleep": 30,
                         "image": "c1700-adventerprisek9-mz.124-25d.image",
                         "mac_addr": "",
                         "mmap": True,
                         "name": "Cisco c1700 appliance",
                         "iomem": 15,
                         "nvram": 128,
                         "platform": "c1700",
                         "chassis": "1760",
                         "private_config": "",
                         "ram": 160,
                         "sparsemem": False,
                         "startup_config": "ios_base_startup-config.txt",
                         "symbol": ":/symbols/router.svg",
                         "system_id": "FTX0945W0MY"}

    for item, value in expected_response.items():
        assert response.json.get(item) == value


def test_c1700_dynamips_appliance_create_wrong_chassis(http_controller):

    params = {"name": "Cisco c1700 appliance",
              "platform": "c1700",
              "chassis": "1770",
              "compute_id": "local",
              "image": "c1700-adventerprisek9-mz.124-25d.image",
              "appliance_type": "dynamips"}

    response = http_controller.post("/appliances", params)
    assert response.status == 400


def test_dynamips_appliance_create_wrong_platform(http_controller):

    params = {"name": "Cisco c3900 appliance",
              "platform": "c3900",
              "compute_id": "local",
              "image": "c3900-test.124-25d.image",
              "appliance_type": "dynamips"}

    response = http_controller.post("/appliances", params)
    assert response.status == 400


def test_iou_appliance_create(http_controller):

    params = {"name": "IOU appliance",
              "compute_id": "local",
              "path": "/path/to/i86bi_linux-ipbase-ms-12.4.bin",
              "appliance_type": "iou"}

    response = http_controller.post("/appliances", params, example=True)
    assert response.status == 201
    assert response.json["appliance_id"] is not None

    expected_response = {"appliance_type": "iou",
                         "builtin": False,
                         "category": "router",
                         "compute_id": "local",
                         "console_auto_start": False,
                         "console_type": "telnet",
                         "default_name_format": "IOU{0}",
                         "ethernet_adapters": 2,
                         "name": "IOU appliance",
                         "nvram": 128,
                         "path": "/path/to/i86bi_linux-ipbase-ms-12.4.bin",
                         "private_config": "",
                         "ram": 256,
                         "serial_adapters": 2,
                         "startup_config": "iou_l3_base_startup-config.txt",
                         "symbol": ":/symbols/multilayer_switch.svg",
                         "use_default_iou_values": True}

    for item, value in expected_response.items():
        assert response.json.get(item) == value


def test_docker_appliance_create(http_controller):

    params = {"name": "Docker appliance",
              "compute_id": "local",
              "image": "gns3/endhost:latest",
              "appliance_type": "docker"}

    response = http_controller.post("/appliances", params, example=True)
    assert response.status == 201
    assert response.json["appliance_id"] is not None

    expected_response = {"adapters": 1,
                         "appliance_type": "docker",
                         "builtin": False,
                         "category": "guest",
                         "compute_id": "local",
                         "console_auto_start": False,
                         "console_http_path": "/",
                         "console_http_port": 80,
                         "console_resolution": "1024x768",
                         "console_type": "telnet",
                         "default_name_format": "{name}-{0}",
                         "environment": "",
                         "extra_hosts": "",
                         "image": "gns3/endhost:latest",
                         "name": "Docker appliance",
                         "start_command": "",
                         "symbol": ":/symbols/docker_guest.svg"}

    for item, value in expected_response.items():
        assert response.json.get(item) == value


def test_qemu_appliance_create(http_controller):

    params = {"name": "Qemu appliance",
              "compute_id": "local",
              "platform": "i386",
              "hda_disk_image": "IOSvL2-15.2.4.0.55E.qcow2",
              "ram": 512,
              "appliance_type": "qemu"}

    response = http_controller.post("/appliances", params, example=True)
    assert response.status == 201
    assert response.json["appliance_id"] is not None

    expected_response = {"adapter_type": "e1000",
                         "adapters": 1,
                         "appliance_type": "qemu",
                         "bios_image": "",
                         "boot_priority": "c",
                         "builtin": False,
                         "category": "guest",
                         "cdrom_image": "",
                         "compute_id": "local",
                         "console_auto_start": False,
                         "console_type": "telnet",
                         "cpu_throttling": 0,
                         "cpus": 1,
                         "default_name_format": "{name}-{0}",
                         "first_port_name": "",
                         "hda_disk_image": "IOSvL2-15.2.4.0.55E.qcow2",
                         "hda_disk_interface": "ide",
                         "hdb_disk_image": "",
                         "hdb_disk_interface": "ide",
                         "hdc_disk_image": "",
                         "hdc_disk_interface": "ide",
                         "hdd_disk_image": "",
                         "hdd_disk_interface": "ide",
                         "initrd": "",
                         "kernel_command_line": "",
                         "kernel_image": "",
                         "legacy_networking": False,
                         "linked_clone": True,
                         "mac_address": "",
                         "name": "Qemu appliance",
                         "on_close": "power_off",
                         "options": "",
                         "platform": "i386",
                         "port_name_format": "Ethernet{0}",
                         "port_segment_size": 0,
                         "process_priority": "normal",
                         "qemu_path": "",
                         "ram": 512,
                         "symbol": ":/symbols/qemu_guest.svg",
                         "usage": "",
                         "custom_adapters": []}

    for item, value in expected_response.items():
        assert response.json.get(item) == value


def test_vmware_appliance_create(http_controller):

    params = {"name": "VMware appliance",
              "compute_id": "local",
              "appliance_type": "vmware",
              "vmx_path": "/path/to/vm.vmx"}

    response = http_controller.post("/appliances", params, example=True)
    assert response.status == 201
    assert response.json["appliance_id"] is not None

    expected_response = {"adapter_type": "e1000",
                         "adapters": 1,
                         "appliance_type": "vmware",
                         "builtin": False,
                         "category": "guest",
                         "compute_id": "local",
                         "console_auto_start": False,
                         "console_type": "none",
                         "default_name_format": "{name}-{0}",
                         "first_port_name": "",
                         "headless": False,
                         "linked_clone": False,
                         "name": "VMware appliance",
                         "on_close": "power_off",
                         "port_name_format": "Ethernet{0}",
                         "port_segment_size": 0,
                         "symbol": ":/symbols/vmware_guest.svg",
                         "use_any_adapter": False,
                         "vmx_path": "/path/to/vm.vmx",
                         "custom_adapters": []}

    for item, value in expected_response.items():
        assert response.json.get(item) == value


def test_virtualbox_appliance_create(http_controller):

    params = {"name": "VirtualBox appliance",
              "compute_id": "local",
              "appliance_type": "virtualbox",
              "vmname": "My VirtualBox VM"}

    response = http_controller.post("/appliances", params, example=True)
    assert response.status == 201
    assert response.json["appliance_id"] is not None

    expected_response = {"adapter_type": "Intel PRO/1000 MT Desktop (82540EM)",
                         "adapters": 1,
                         "appliance_type": "virtualbox",
                         "builtin": False,
                         "category": "guest",
                         "compute_id": "local",
                         "console_auto_start": False,
                         "console_type": "none",
                         "default_name_format": "{name}-{0}",
                         "first_port_name": "",
                         "headless": False,
                         "linked_clone": False,
                         "name": "VirtualBox appliance",
                         "on_close": "power_off",
                         "port_name_format": "Ethernet{0}",
                         "port_segment_size": 0,
                         "ram": 256,
                         "symbol": ":/symbols/vbox_guest.svg",
                         "use_any_adapter": False,
                         "vmname": "My VirtualBox VM",
                         "custom_adapters": []}

    for item, value in expected_response.items():
        assert response.json.get(item) == value

def test_vpcs_appliance_create(http_controller):

    params = {"name": "VPCS appliance",
              "compute_id": "local",
              "appliance_type": "vpcs"}

    response = http_controller.post("/appliances", params, example=True)
    assert response.status == 201
    assert response.json["appliance_id"] is not None

    expected_response = {"appliance_type": "vpcs",
                         "base_script_file": "vpcs_base_config.txt",
                         "builtin": False,
                         "category": "guest",
                         "compute_id": "local",
                         "console_auto_start": False,
                         "console_type": "telnet",
                         "default_name_format": "PC{0}",
                         "name": "VPCS appliance",
                         "symbol": ":/symbols/vpcs_guest.svg"}

    for item, value in expected_response.items():
        assert response.json.get(item) == value

def test_ethernet_switch_appliance_create(http_controller):

    params = {"name": "Ethernet switch appliance",
              "compute_id": "local",
              "appliance_type": "ethernet_switch"}

    response = http_controller.post("/appliances", params, example=True)
    assert response.status == 201
    assert response.json["appliance_id"] is not None

    expected_response = {"appliance_type": "ethernet_switch",
                         "builtin": False,
                         "category": "switch",
                         "compute_id": "local",
                         "console_type": "telnet",
                         "default_name_format": "Switch{0}",
                         "name": "Ethernet switch appliance",
                         "ports_mapping": [{"ethertype": "",
                                            "name": "Ethernet0",
                                            "port_number": 0,
                                            "type": "access",
                                            "vlan": 1
                                            },
                                           {"ethertype": "",
                                            "name": "Ethernet1",
                                            "port_number": 1,
                                            "type": "access",
                                            "vlan": 1
                                            },
                                           {"ethertype": "",
                                            "name": "Ethernet2",
                                            "port_number": 2,
                                            "type": "access",
                                            "vlan": 1
                                            },
                                           {"ethertype": "",
                                            "name": "Ethernet3",
                                            "port_number": 3,
                                            "type": "access",
                                            "vlan": 1
                                            },
                                           {"ethertype": "",
                                            "name": "Ethernet4",
                                            "port_number": 4,
                                            "type": "access",
                                            "vlan": 1
                                            },
                                           {"ethertype": "",
                                            "name": "Ethernet5",
                                            "port_number": 5,
                                            "type": "access",
                                            "vlan": 1
                                            },
                                           {"ethertype": "",
                                            "name": "Ethernet6",
                                            "port_number": 6,
                                            "type": "access",
                                            "vlan": 1
                                            },
                                           {"ethertype": "",
                                            "name": "Ethernet7",
                                            "port_number": 7,
                                            "type": "access",
                                            "vlan": 1
                                            }],
                         "symbol": ":/symbols/ethernet_switch.svg"}

    for item, value in expected_response.items():
        assert response.json.get(item) == value


def test_cloud_appliance_create(http_controller):

    params = {"name": "Cloud appliance",
              "compute_id": "local",
              "appliance_type": "cloud"}

    response = http_controller.post("/appliances", params, example=True)
    assert response.status == 201
    assert response.json["appliance_id"] is not None

    expected_response = {"appliance_type": "cloud",
                         "builtin": False,
                         "category": "guest",
                         "compute_id": "local",
                         "default_name_format": "Cloud{0}",
                         "name": "Cloud appliance",
                         "symbol": ":/symbols/cloud.svg"}

    for item, value in expected_response.items():
        assert response.json.get(item) == value


def test_ethernet_hub_appliance_create(http_controller):

    params = {"name": "Ethernet hub appliance",
              "compute_id": "local",
              "appliance_type": "ethernet_hub"}

    response = http_controller.post("/appliances", params, example=True)
    assert response.status == 201
    assert response.json["appliance_id"] is not None

    expected_response = {"ports_mapping": [{"port_number": 0,
                                            "name": "Ethernet0"
                                            },
                                           {"port_number": 1,
                                             "name": "Ethernet1"
                                            },
                                           {"port_number": 2,
                                            "name": "Ethernet2"
                                            },
                                           {"port_number": 3,
                                            "name": "Ethernet3"
                                            },
                                           {"port_number": 4,
                                            "name": "Ethernet4"
                                            },
                                           {"port_number": 5,
                                            "name": "Ethernet5"
                                            },
                                           {"port_number": 6,
                                            "name": "Ethernet6"
                                            },
                                           {"port_number": 7,
                                            "name": "Ethernet7"
                                            }],
                         "compute_id": "local",
                         "name": "Ethernet hub appliance",
                         "symbol": ":/symbols/hub.svg",
                         "default_name_format": "Hub{0}",
                         "appliance_type": "ethernet_hub",
                         "category": "switch",
                         "builtin": False}

    for item, value in expected_response.items():
        assert response.json.get(item) == value


def test_create_node_from_appliance(http_controller, controller, project, compute):

    id = str(uuid.uuid4())
    controller._appliances = {id: Appliance(id, {
        "appliance_type": "qemu",
        "category": 0,
        "name": "test",
        "symbol": "guest.svg",
        "default_name_format": "{name}-{0}",
        "compute_id": "example.com"
    })}
    with asyncio_patch("gns3server.controller.project.Project.add_node_from_appliance") as mock:
        response = http_controller.post("/projects/{}/appliances/{}".format(project.id, id), {
            "x": 42,
            "y": 12
        })
    mock.assert_called_with(id, x=42, y=12, compute_id=None)
    assert response.route == "/projects/{project_id}/appliances/{appliance_id}"
    assert response.status == 201
