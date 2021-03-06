# Copyright 2012 OpenStack LLC.
# All Rights Reserved
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
#
# vim: tabstop=4 shiftwidth=4 softtabstop=4

import argparse
import logging

from quantumclient.common import utils
from quantumclient.quantum.v2_0 import CreateCommand
from quantumclient.quantum.v2_0 import DeleteCommand
from quantumclient.quantum.v2_0 import ListCommand
from quantumclient.quantum.v2_0 import ShowCommand
from quantumclient.quantum.v2_0 import UpdateCommand


def _format_subnets(network):
    try:
        return '\n'.join([' '.join([s['id'], s.get('cidr', '')])
                          for s in network['subnets']])
    except Exception:
        return ''


class ListNetwork(ListCommand):
    """List networks that belong to a given tenant."""

    resource = 'network'
    log = logging.getLogger(__name__ + '.ListNetwork')
    _formatters = {'subnets': _format_subnets, }
    list_columns = ['id', 'name', 'subnets']

    def extend_list(self, data, parsed_args):
        """Add subnet information to a network list"""
        quantum_client = self.get_client()
        search_opts = {'fields': ['id', 'cidr']}
        subnets = quantum_client.list_subnets(**search_opts).get('subnets', [])
        subnet_dict = dict([(s['id'], s) for s in subnets])
        for n in data:
            if 'subnets' in n:
                n['subnets'] = [(subnet_dict.get(s) or {"id": s})
                                for s in n['subnets']]


class ListExternalNetwork(ListNetwork):
    """List external networks that belong to a given tenant"""

    log = logging.getLogger(__name__ + '.ListExternalNetwork')

    def retrieve_list(self, parsed_args):
        external = '--router:external=True'
        if external not in self.values_specs:
            self.values_specs.append('--router:external=True')
        return super(ListExternalNetwork, self).retrieve_list(parsed_args)


class ShowNetwork(ShowCommand):
    """Show information of a given network."""

    resource = 'network'
    log = logging.getLogger(__name__ + '.ShowNetwork')


class CreateNetwork(CreateCommand):
    """Create a network for a given tenant."""

    resource = 'network'
    log = logging.getLogger(__name__ + '.CreateNetwork')

    def add_known_arguments(self, parser):
        parser.add_argument(
            '--admin-state-down',
            default=True, action='store_false',
            help='Set Admin State Up to false')
        parser.add_argument(
            '--admin_state_down',
            action='store_false',
            help=argparse.SUPPRESS)
        parser.add_argument(
            '--shared',
            action='store_true',
            default=argparse.SUPPRESS,
            help='Set the network as shared')
        parser.add_argument(
            'name', metavar='NAME',
            help='Name of network to create')

    def args2body(self, parsed_args):
        body = {'network': {
            'name': parsed_args.name,
            'admin_state_up': parsed_args.admin_state_down}, }
        if parsed_args.tenant_id:
            body['network'].update({'tenant_id': parsed_args.tenant_id})
        if hasattr(parsed_args, 'shared'):
            body['network'].update({'shared': parsed_args.shared})
        return body


class DeleteNetwork(DeleteCommand):
    """Delete a given network."""

    log = logging.getLogger(__name__ + '.DeleteNetwork')
    resource = 'network'


class UpdateNetwork(UpdateCommand):
    """Update network's information."""

    log = logging.getLogger(__name__ + '.UpdateNetwork')
    resource = 'network'
