# Copyright 2014: Mirantis Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import mock

from rally.benchmark.scenarios.sahara import clusters
from tests.unit import test

SAHARA_CLUSTERS = "rally.benchmark.scenarios.sahara.clusters.SaharaClusters"
SAHARA_UTILS = 'rally.benchmark.scenarios.sahara.utils'


class SaharaClustersTestCase(test.TestCase):

    @mock.patch(SAHARA_CLUSTERS + "._delete_cluster")
    @mock.patch(SAHARA_CLUSTERS + "._launch_cluster",
                return_value=mock.MagicMock(id=42))
    @mock.patch(SAHARA_UTILS + '.SaharaScenario.clients')
    def test_create_and_delete_cluster(self, mock_clients, mock_launch_cluster,
                                       mock_delete_cluster):

        clusters_scenario = clusters.SaharaClusters()

        clusters_scenario.context = {
            "tenant": {
                "sahara_image": "test_image"
            }
        }
        clusters_scenario.create_and_delete_cluster(
            flavor="test_flavor",
            node_count=5,
            plugin_name="test_plugin",
            hadoop_version="test_version")

        mock_launch_cluster.assert_called_once_with(
            flavor_id="test_flavor",
            image_id="test_image",
            node_count=5,
            plugin_name="test_plugin",
            hadoop_version="test_version",
            floating_ip_pool=None,
            neutron_net_id=None,
            volumes_per_node=None,
            volumes_size=None,
            auto_security_group=None,
            security_groups=None,
            node_configs=None,
            cluster_configs=None)

        mock_delete_cluster.assert_called_once_with(
            mock_launch_cluster.return_value)

    @mock.patch(SAHARA_CLUSTERS + "._delete_cluster")
    @mock.patch(SAHARA_CLUSTERS + "._scale_cluster")
    @mock.patch(SAHARA_CLUSTERS + "._launch_cluster",
                return_value=mock.MagicMock(id=42))
    @mock.patch(SAHARA_UTILS + '.SaharaScenario.clients')
    def test_create_scale_delete_cluster(self, mock_clients,
                                         mock_launch_cluster,
                                         mock_scale_cluster,
                                         mock_delete_cluster):

        mock_sahara = mock_clients("sahara")
        mock_sahara.clusters.get.return_value = mock.MagicMock(
            id=42, status="active"
        )
        clusters_scenario = clusters.SaharaClusters()

        clusters_scenario.context = {
            "tenant": {
                "sahara_image": "test_image"
            }
        }

        clusters_scenario.create_scale_delete_cluster(
            flavor="test_flavor",
            node_count=5,
            deltas=[1, -1],
            plugin_name="test_plugin",
            hadoop_version="test_version")

        mock_launch_cluster.assert_called_once_with(
            flavor_id="test_flavor",
            image_id="test_image",
            node_count=5,
            plugin_name="test_plugin",
            hadoop_version="test_version",
            floating_ip_pool=None,
            neutron_net_id=None,
            volumes_per_node=None,
            volumes_size=None,
            auto_security_group=None,
            security_groups=None,
            node_configs=None,
            cluster_configs=None)

        mock_scale_cluster.assert_has_calls([
            mock.call(mock_sahara.clusters.get.return_value, 1),
            mock.call(mock_sahara.clusters.get.return_value, -1),
        ])

        mock_delete_cluster.assert_called_once_with(
            mock_sahara.clusters.get.return_value)
