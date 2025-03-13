#!/bin/sh
command="$1"
shift
files="${@}"
export CI=true
run_docker="$(docker --version)";
docker_status=${?}

run_unittest(){

    if [ "${docker_status}" -eq "0" ]; then

	docker-compose \
	    -f docker-compose.yml \
	    -f docker-compose-remote-dev.yml \
	    -f docker-compose.override.yml \
	    exec \
	    -T \
	    -e DJANGO_SETTINGS_MODULE=config.settings.testing \
	    web \
	    pytest \
	    -q \
	    -v \
	    -m 'not functional'
	exit ${?}
    fi

    bash -c "DJANGO_SETTINGS_MODULE=config.settings.testing pytest -v -m 'not functional'"
    exit ${?}
}


run_pylint(){

    if [ "${docker_status}" -eq "0" ]; then
    
	docker-compose \
	    -f docker-compose.yml \
	    -f docker-compose-remote-dev.yml \
	    -f docker-compose.override.yml \
	    exec \
	    -T \
	    -e DJANGO_SETTINGS_MODULE=config.settings.testing \
	    web \
	    pylint \
            --load-plugins=pylint_django,pylint_django.checkers.migrations \
            --rcfile=pyproject.toml \
	    ${files}

	exit ${?}
    fi

    pylint \
    --load-plugins=pylint_django,pylint_django.checkers.migrations \
    --rcfile=pyproject.toml \
    ${files}
    exit ${?}
}

if [ "${command}" = "run_unittest" ]; then
    run_unittest;
fi
if [ "${command}" = "run_pylint" ]; then
    run_pylint;
fi
