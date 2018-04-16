#!/bin/bash

cat > requirements.txt

# Compile wheels
for PYBIN in /opt/python/cp36-cp36m/bin; do
    ${PYBIN}/pip wheel -w wheels -r requirements.txt > /dev/null
done

mkdir repaired-wheels

# Bundle external shared libraries into the wheels
for whl in wheels/*.whl; do
    auditwheel repair $whl -w repaired-wheels > /dev/null 2> /dev/null
done

tar -c repaired-wheels/*
