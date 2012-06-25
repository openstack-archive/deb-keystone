
#!/bin/sh
# Script to create base roles on keystone database
set -e

# ToDo: Check service is running and token properly set


SERVICE_TOKEN={`gawk 'match ($0, /^admin_token\s?=\s?(.*)/, ary){ print ary[1]}' /etc/keystone/keystone.conf`:-"ADMIN"}
SERVICE_ENDPOINT="http://localhost:35357/v2.0/"


if ! timeout 20 sh -c "while ! http_proxy= wget -q -O- ${SERVICE_ENDPOINT}; do sleep 1; done"
then
        echo "keystone not running"
        exit 1
fi


create_role() {
    id=`keystone role-list | grep " $1 " | awk '{ print $2 }'`
    if [ -z $id ]; then
        id=`keystone role-create --name=$1 | grep " id " | awk '{ print $4 }'`
        echo "Created role $1 with id $id"
    fi
}

get_id() {
    keystone $1-list | grep " $2 " | awk '{ print $2 }'
}

create_role admin
create_role Member
create_role KeystoneAdmin
create_role KeystoneServiceAdmin
create_role sysadmin
create_role netadmin

ADMIN_TENANT=`keystone tenant-create --name=admin | awk '/ id / { print $4 }'`
DEMO_TENANT=`keystone tenant-create --name=demo | awk '/ id / { print $4 }'`
SERVICE_TENANT=`keystone tenant-create --name=service | awk '/ id / { print $4 }'`

keystone user-create --name=admin --pass="admin" --email=admin@example.com
keystone user-create --name=demo --pass="demo" --email=admin@example.com

ADMIN_ROLE=`get_id role admin`
MEMBER_ROLE=`get_id role Member`
SYSADMIN_ROLE=`get_id role sysadmin`
NETADMIN_ROLE=`get_id role netadmin`
ADMIN_USER=`get_id user admin`
DEMO_USER=`get_id user demo`

keystone user-role-add --user $ADMIN_USER --role $ADMIN_ROLE --tenant_id $ADMIN_TENANT
keystone user-role-add --user $ADMIN_USER --role $ADMIN_ROLE --tenant_id $DEMO_TENANT
keystone user-role-add --user $DEMO_USER --role $MEMBER_ROLE --tenant_id $DEMO_TENANT
keystone user-role-add --user $DEMO_USER --role $SYSADMIN_ROLE --tenant_id $DEMO_TENANT
keystone user-role-add --user $DEMO_USER --role $NETADMIN_ROLE --tenant_id $DEMO_TENANT

keystone service-create --name=nova --type=compute --description="Nova Compute Service"
NOVA_USER=`keystone user-create --name=nova --pass="nova" --email=nova@example.com |  awk '/ id / { print $4 }'`
keystone user-role-add --user $NOVA_USER --role $ADMIN_ROLE --tenant_id $SERVICE_TENANT
keystone service-create --name=ec2 --type=ec2 --description="EC2 Compatibility Layer"
keystone service-create --name=glance --type=image --description="Glance Image Service"
GLANCE_USER=`keystone user-create --name=glance --pass="glance" --email=glance@example.com |  awk '/ id / { print $4 }'`
keystone user-role-add --user $GLANCE_USER --role $ADMIN_ROLE --tenant_id $SERVICE_TENANT
keystone service-create --name=keystone --type=identity --description="Keystone Identity Service"

# Use only whit quantum networking
#keystone service-create --name=quantum --type=network --description="Quantum Service"
