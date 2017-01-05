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

import asyncio
import aiohttp


from .link import Link


class UDPLink(Link):

    def __init__(self, project, link_id=None):
        super().__init__(project, link_id=link_id)
        self._capture_node = None
        self._created = False
        self._link_data = []

    @property
    def debug_link_data(self):
        """
        Use for the debug exports
        """
        return self._link_data

    @asyncio.coroutine
    def create(self):
        """
        Create the link on the nodes
        """

        node1 = self._nodes[0]["node"]
        adapter_number1 = self._nodes[0]["adapter_number"]
        port_number1 = self._nodes[0]["port_number"]
        node2 = self._nodes[1]["node"]
        adapter_number2 = self._nodes[1]["adapter_number"]
        port_number2 = self._nodes[1]["port_number"]

        # Get an IP allowing communication between both host
        try:
            (node1_host, node2_host) = yield from node1.compute.get_ip_on_same_subnet(node2.compute)
        except ValueError as e:
            raise aiohttp.web.HTTPConflict(text=str(e))

        # Reserve a UDP port on both side
        response = yield from node1.compute.post("/projects/{}/ports/udp".format(self._project.id))
        self._node1_port = response.json["udp_port"]
        response = yield from node2.compute.post("/projects/{}/ports/udp".format(self._project.id))
        self._node2_port = response.json["udp_port"]

        # Create the tunnel on both side
        self._link_data.append({
            "lport": self._node1_port,
            "rhost": node2_host,
            "rport": self._node2_port,
            "type": "nio_udp"
        })
        yield from node1.post("/adapters/{adapter_number}/ports/{port_number}/nio".format(adapter_number=adapter_number1, port_number=port_number1), data=self._link_data[0], timeout=120)

        self._link_data.append({
            "lport": self._node2_port,
            "rhost": node1_host,
            "rport": self._node1_port,
            "type": "nio_udp"
        })
        try:
            yield from node2.post("/adapters/{adapter_number}/ports/{port_number}/nio".format(adapter_number=adapter_number2, port_number=port_number2), data=self._link_data[1], timeout=120)
        except Exception as e:
            # We clean the first NIO
            yield from node1.delete("/adapters/{adapter_number}/ports/{port_number}/nio".format(adapter_number=adapter_number1, port_number=port_number1), timeout=120)
            raise e
        self._created = True

    @asyncio.coroutine
    def delete(self):
        """
        Delete the link and free the resources
        """
        if not self._created:
            return
        try:
            node1 = self._nodes[0]["node"]
            adapter_number1 = self._nodes[0]["adapter_number"]
            port_number1 = self._nodes[0]["port_number"]
        except IndexError:
            return
        try:
            yield from node1.delete("/adapters/{adapter_number}/ports/{port_number}/nio".format(adapter_number=adapter_number1, port_number=port_number1), timeout=120)
        # If the node is already delete (user selected multiple element and delete all in the same time)
        except aiohttp.web.HTTPNotFound:
            pass

        try:
            node2 = self._nodes[1]["node"]
            adapter_number2 = self._nodes[1]["adapter_number"]
            port_number2 = self._nodes[1]["port_number"]
        except IndexError:
            return
        try:
            yield from node2.delete("/adapters/{adapter_number}/ports/{port_number}/nio".format(adapter_number=adapter_number2, port_number=port_number2), timeout=120)
        # If the node is already delete (user selected multiple element and delete all in the same time)
        except aiohttp.web.HTTPNotFound:
            pass
        yield from super().delete()

    @asyncio.coroutine
    def start_capture(self, data_link_type="DLT_EN10MB", capture_file_name=None):
        """
        Start capture on a link
        """
        if not capture_file_name:
            capture_file_name = self.default_capture_file_name()
        self._capture_node = self._choose_capture_side()
        data = {
            "capture_file_name": capture_file_name,
            "data_link_type": data_link_type
        }
        yield from self._capture_node["node"].post("/adapters/{adapter_number}/ports/{port_number}/start_capture".format(adapter_number=self._capture_node["adapter_number"], port_number=self._capture_node["port_number"]), data=data)
        yield from super().start_capture(data_link_type=data_link_type, capture_file_name=capture_file_name)

    @asyncio.coroutine
    def stop_capture(self):
        """
        Stop capture on a link
        """
        if self._capture_node:
            yield from self._capture_node["node"].post("/adapters/{adapter_number}/ports/{port_number}/stop_capture".format(adapter_number=self._capture_node["adapter_number"], port_number=self._capture_node["port_number"]))
            self._capture_node = None
        yield from super().stop_capture()

    def _choose_capture_side(self):
        """
        Run capture on the best candidate.

        The ideal candidate is a node who on controller server and always
        running (capture will not be cut off)

        :returns: Node where the capture should run
        """

        ALWAYS_RUNNING_NODES_TYPE = ("cloud", "nat", "ethernet_switch", "ethernet_hub")

        for node in self._nodes:
            if node["node"].compute.id == "local" and node["node"].node_type in ALWAYS_RUNNING_NODES_TYPE and node["node"].status == "started":
                return node

        for node in self._nodes:
            if node["node"].node_type in ALWAYS_RUNNING_NODES_TYPE and node["node"].status == "started":
                return node

        for node in self._nodes:
            if node["node"].compute.id == "local" and node["node"].status == "started":
                return node

        for node in self._nodes:
            if node["node"].node_type and node["node"].status == "started":
                return node

        raise aiohttp.web.HTTPConflict(text="Can not capture because no running device on this link")

    @asyncio.coroutine
    def read_pcap_from_source(self):
        """
        Return a FileStream of the Pcap from the compute node
        """
        if self._capture_node:
            compute = self._capture_node["node"].compute
            return compute.stream_file(self._project, "tmp/captures/" + self._capture_file_name)

    @asyncio.coroutine
    def node_updated(self, node):
        """
        Called when a node member of the link is updated
        """
        if self._capture_node and node == self._capture_node["node"] and node.status != "started":
            yield from self.stop_capture()
