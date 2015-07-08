#
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain
#   a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#

"""Volume V2 Volume action implementations"""

import argparse
import logging
import six

from cliff import command
from cliff import show
import six

from openstackclient.common import parseractions
from openstackclient.common import utils


class CreateVolume(show.ShowOne):
    """Create new volume"""

    log = logging.getLogger(__name__ + '.CreateVolume')

    def get_parser(self, prog_name):
        parser = super(CreateVolume, self).get_parser(prog_name)
        parser.add_argument(
            'project',
            metavar='<project>',
            help='Specify an alternate project (name or ID)',
        )
        parser.add_argument(
            '--availability-zone',
            metavar='<availability-zone>',
            help='Create new volume in <availability-zone>',
        )
        parser.add_argument(
            '--source_volid',
            metavar='<source_volid>',
            help='To create a volume from an existing volume, specify the <source_volid> of the existing volume.'
                 'The volume is created with the same size as the source volume.',
        )
        parser.add_argument(
            '--description',
            metavar='<description>',
            help='New volume description',
        )
        parser.add_argument(
            '--snapshot-id',
            metavar='<snapshot-id>',
            help=argparse.SUPPRESS,
        )
        parser.add_argument(
            '--size',
            metavar='<size>',
            required=True,
            type=int,
            help='New volume size in GB',
        )
        parser.add_argument(
            '--name',
            metavar='<name>',
            help='New volume name',
        )
        parser.add_argument(
            '--imageRef',
            metavar='<imageReg>',
            help='The ID of the <imageReg> from which you want to create the volume. Required to create a bootable volume.',
        )
        parser.add_argument(
            '--volume_type',
            metavar='<volume-type>',
            help='Use <volume-type> as the new volume type',
        )
        parser.add_argument(
            '--metadata' ,
            metavar='<key=value>',
            action=parseractions.KeyValueAction,
            help='Set a property on this volume '
                 '(repeat option to set multiple properties)',
        )
        parser.add_argument(
            '--user',
            metavar='<user>',
            help='<user> ID',
        )

        return parser


    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)

        identity_client = self.app.client_manager.identity
        image_client = self.app.client_manager.image
        volume_client = self.app.client_manager.volume

        source_volume = None
        if parsed_args.source_volid:
            source_volume = utils.find_resource(
                volume_client.volumes,
                parsed_args.source_volid,
            ).id

        project = None
        if parsed_args.project:
            project = utils.find_resource(
                identity_client.projects,
                parsed_args.project,
            ).id

        image = None
        if parsed_args.imageRef:
            image = image_client.images.get(parsed_args.imageRef)

        snapshot = parsed_args.snapshot_id

        volume = volume_client.volumes.create(
            parsed_args.size,
            snapshot,
            source_volume,
            parsed_args.name,
            parsed_args.description,
            parsed_args.volume_type,
            parsed_args.user,
            project,
            parsed_args.availability_zone,
            parsed_args.metadata,
            image.id,
        )
        # Map 'metadata' column to 'properties'
        volume._info.update(
            {
                'properties': utils.format_dict(volume._info.pop('metadata')),
                'type': volume._info.pop('volume_type'),
            },
        )

        return zip(*sorted(six.iteritems(volume._info)))


class DeleteVolume(command.Command):
    """Delete volume(s)"""

    log = logging.getLogger(__name__ + ".DeleteVolume")

    def get_parser(self, prog_name):
        parser = super(DeleteVolume, self).get_parser(prog_name)
        parser.add_argument(
            "volumes",
            metavar="<volume>",
            nargs="+",
            help="Volume(s) to delete (name or ID)"
        )
        parser.add_argument(
            "--force",
            dest="force",
            action="store_true",
            default=False,
            help="Attempt forced removal of volume(s), regardless of state "
                 "(defaults to False"
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug("take_action: (%s)", parsed_args)
        volume_client = self.app.client_manager.volume
        for volume in parsed_args.volumes:
            volume_obj = utils.find_resource(
                volume_client.volumes, volume)
        if parsed_args.force:
            volume_client.volumes.force_delete(volume_obj.id)
        else:
            volume_client.volumes.delete(volume_obj.id)
        return


class ShowVolume(show.ShowOne):
    """Display volume details"""

    log = logging.getLogger(__name__ + '.ShowVolume')

    def get_parser(self, prog_name):
        parser = super(ShowVolume, self).get_parser(prog_name)
        parser.add_argument(
            'volume',
            metavar="<volume-id>",
            help="Volume to display (name or ID)"
        )
        return parser

    def take_action(self, parsed_args):
        self.log.debug('take_action(%s)', parsed_args)
        volume_client = self.app.client_manager.volume
        volume = utils.find_resource(volume_client.volumes, parsed_args.volume)

        # Remove key links from being displayed
        volume._info.pop("links", None)
        return zip(*sorted(six.iteritems(volume._info)))
