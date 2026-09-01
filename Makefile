# Comandos de django

migrate:
		./.vwlili/bin/python src/manage.py migrate

migrations:
		./.vwlili/bin/python src/manage.py makemigrations

test-server:
		./.vwlili/bin/python src/manage.py runserver 8001


# Comandos de testeo
test:
		./.vwlili/bin/pytest tests

test-functional:
		./.vwlili/bin/pytest tests/functional

test-unit:
		./.vwlili/bin/pytest tests/unit

test-staging:
		DJANGO_TEST_TOKEN="ooio4903_4uu3u_4rui344u890" \
		TEST_SERVER=staging.lilianamedela.com.ar \
		DJANGO_TEST_ADMIN_USERNAME=admin \
		DJANGO_TEST_ADMIN_PASSWORD=pasparafrasia \
		.vwlili/bin/pytest tests/functional/remote


# Comandos de deploy (ansible-playbook)

pull:
		./.vwlili/bin/ansible-playbook -i infra/inventory infra/pull-from-server-playbook.yaml

data-backup:
		./.vwlili/bin/ansible-playbook infra/data-backup-playbook.yaml

data-restore:
		./.vwlili/bin/ansible-playbook infra/data-restore-playbook.yaml

data-restore-anterior:
		./.vwlili/bin/ansible-playbook infra/data-restore-playbook.yaml -e "backup_version=1"

data-restore-mas-antiguo:
		./.vwlili/bin/ansible-playbook infra/data-restore-playbook.yaml -e "backup_version=2"

db-restore:
		./.vwlili/bin/ansible-playbook infra/data-restore-playbook.yaml -e "restore_media=false"

deploy:
		./.vwlili/bin/ansible-playbook infra/deploy-remote-playbook.yaml

deploy-staging:
		./.vwlili/bin/ansible-playbook infra/deploy-remote-playbook.yaml -e "site_env=staging"

media-restore:
		./.vwlili/bin/ansible-playbook infra/data-restore-playbook.yaml -e "restore_db=false"

staging-off:
		./.vwlili/bin/ansible-playbook infra/staging-manage-playbook.yaml -e "accion=stop"

staging-on:
		./.vwlili/bin/ansible-playbook infra/staging-manage-playbook.yaml -e "accion=start"


# Comandos de control de versiones
tag-live:
		git tag -f LIVE && export TAG=`date +DEPLOYED-%F/%H%M` && git tag $TAG && git push -f LIVE $TAG
