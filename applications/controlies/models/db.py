# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations
import logging, logging.handlers
import os

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
#########################################################################

if request.env.web2py_runtime_gae:            # if running on Google App Engine
    db = DAL('gae')                           # connect to Google BigTable
                                              # optional DAL('gae://namespace')
    session.connect(request, response, db = db) # and store sessions and tickets there
    ### or use the following lines to store sessions in Memcache
    # from gluon.contrib.memdb import MEMDB
    # from google.appengine.api.memcache import Client
    # session.connect(request, response, db = MEMDB(Client()))
else:                                         # else use a normal relational database
    db = DAL('sqlite://storage.sqlite')       # if not, use SQLite or other DB
## if no need for session
# session.forget()

#########################################################################
## Here is sample code if you need for
## - email capabilities
## - authentication (registration, login, logout, ... )
## - authorization (role based authorization)
## - services (xml, csv, json, xmlrpc, jsonrpc, amf, rss)
## - crud actions
## (more options discussed in gluon/tools.py)
#########################################################################

from gluon.tools import *
from gluon.contrib.login_methods.ldap_auth import ldap_auth




mail = Mail()                                  # mailer
auth = Auth(globals(),db)                      # authentication/authorization
crud = Crud(globals(),db)                      # for CRUD helpers using auth
service = Service(globals())                   # for json, xml, jsonrpc, xmlrpc, amfrpc
plugins = PluginManager()

auth.define_tables(username=True)


mail.settings.server = 'logging' or 'smtp.gmail.com:587'  # your SMTP server
mail.settings.sender = 'you@gmail.com'         # your email
mail.settings.login = 'username:password'      # your credentials or None

auth.settings.hmac_key = 'sha512:f649047b-106d-4ef5-ba95-ac9d43734978'   # before define_tables()
auth.define_tables()                           # creates all needed tables
auth.settings.mailer = mail                    # for user email verification
auth.settings.registration_requires_verification = True
auth.settings.registration_requires_approval = True
auth.messages.verify_email = 'Click on the link http://'+request.env.http_host+URL('default','user',args=['verify_email'])+'/%(key)s to verify your email'
auth.settings.reset_password_requires_verification = True
#auth.settings.alternate_requires_registration = True 
auth.messages.reset_password = 'Click on the link http://'+request.env.http_host+URL('default','user',args=['reset_password'])+'/%(key)s to reset your password'

#########################################################################
## If you need to use OpenID, Facebook, MySpace, Twitter, Linkedin, etc.
## register with janrain.com, uncomment and customize following
# from gluon.contrib.login_methods.rpx_account import RPXAccount
# auth.settings.actions_disabled=['register','change_password','request_reset_password']
auth.settings.actions_disabled=['register','profile','request_reset_password','retrieve_username']
# auth.settings.login_form = RPXAccount(request, api_key='...',domain='...',
#    url = "http://localhost:8000/%s/default/user/login" % request.application)
## other login methods are in gluon/contrib/login_methods
#########################################################################

crud.settings.auth = None                      # =auth to enforce authorization on crud

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################


#########################################################
#
# Global functions
#
#########################################################

prod = cache.ram('prod', lambda : bool(os.environ.get('PRODUCTION')), time_expire=5000)

if prod == False:
    #
    # Development environment
    #
    log_level = logging.DEBUG

else:
    #
    # Production environment
    #
    log_level = logging.ERROR

    

#
# Logger
#

def get_configured_logger(name):
    logger = logging.getLogger(name)
    if (len(logger.handlers) == 0):
        # Create RotatingFileHandler
        import os
        formatter="%(asctime)s %(levelname)s %(process)s %(thread)s %(funcName)s():%(lineno)d %(message)s"
        handler = logging.handlers.RotatingFileHandler(os.path.join(request.folder,'private/app.log'),maxBytes=1024,backupCount=2)
        handler.setFormatter(logging.Formatter(formatter))
        # setting level
        handler.setLevel(log_level)
        logger.addHandler(handler)
        logger.setLevel(log_level)
        logger.debug(name + ' logger created')
        if str(prod) == True:
            logger.debug('Server launched in production mode')
        else:
            logger.debug('Server launched in developpment mode')
    return logger

logger = cache.ram('once',lambda:get_configured_logger(request.application),time_expire=99999999)


def conecta():
    l=LdapConnection.LdapConnection(session)
    l.process()
    return l

def right_firefox_version(user_agent):
    right=True
    if "Mozilla" in user_agent:
        k=user_agent.split("Firefox/")
        if len(k)<2 : k=user_agent.split("Iceweasel/")
        if len(k)>1:
            version=k[1].split()[0]
            if version <"4.0": right=False #firefox<4
    return right

            
    
    
