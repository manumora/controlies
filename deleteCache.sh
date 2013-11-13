rm -rf applications/controlies/cache/*
rm -rf applications/controlies/databases/*
rm -rf applications/controlies/errors/*
rm -rf applications/controlies/private/*
rm -rf applications/controlies/sessions/*
rm -rf debian/controlies
rm -rf debian/controlies-thinclient
rm -rf debian/controlies-client
rm -rf debian/controlies.debhelper.log
rm -rf debian/controlies-thinclient.debhelper.log
rm -rf debian/controlies-client.debhelper.log
rm -rf debian/controlies.substvars
rm -rf debian/controlies-thinclient.substvars
rm -rf debian/controlies-client.substvars
rm -rf debian/files
find ./ -iname "*.pyc" -print0 | xargs -0 rm -rf
