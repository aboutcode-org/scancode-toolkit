# -------------------------------------------------------------------------- #
# Copyright 2002-2015, OpenNebula Project (OpenNebula.org), C12G Labs        #
#                                                                            #
# Licensed under the Apache License, Version 2.0 (the "License"); you may    #
# not use this file except in compliance with the License. You may obtain    #
# a copy of the License at                                                   #
#                                                                            #
# http://www.apache.org/licenses/LICENSE-2.0                                 #
#                                                                            #
# Unless required by applicable law or agreed to in writing, software        #
# distributed under the License is distributed on an "AS IS" BASIS,          #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.   #
# See the License for the specific language governing permissions and        #
# limitations under the License.                                             #
#--------------------------------------------------------------------------- #

require 'cli_helper'

begin
    require 'opennebula'
rescue Exception => e
    puts "Error: "+e.message.to_s
    exit(-1)
end

include OpenNebula

module OpenNebulaHelper
    ONE_VERSION=<<-EOT
OpenNebula #{OpenNebula::VERSION}
Copyright 2002-2015, OpenNebula Project (OpenNebula.org), C12G Labs

Licensed under the Apache License, Version 2.0 (the "License"); you may
not use this file except in compliance with the License. You may obtain
a copy of the License at http://www.apache.org/licenses/LICENSE-2.0
EOT

    if ONE_LOCATION
        TABLE_CONF_PATH=ONE_LOCATION+"/etc/cli"
    else
        TABLE_CONF_PATH="/etc/one/cli"
    end

