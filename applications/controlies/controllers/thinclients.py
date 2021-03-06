# coding: utf8
from applications.controlies.modules.Thinclients import Thinclients
from applications.controlies.modules.Users import Users
from applications.controlies.modules.Groups import Groups
from applications.controlies.modules.Laptops import Laptops
from applications.controlies.modules.LaptopsHistory import LaptopsHistory

def index():
    if not auth.user: redirect(URL(c='default'))
    return dict()
    
@service.json
def getHostData():
    l=conecta()
    h = Thinclients(l,request.vars['name'])
    response = h.getHostData()    
    l.close()
    return dict(response=response)
    
@service.json   
@auth.requires_login()
def list():
    l=conecta()
    h = Thinclients (l)
    a=request.vars
    response = h.list(a)    
    l.close()
    return response    

@service.json
@auth.requires_login()
def modify():
    l=conecta()
    h = Thinclients(l,request.vars['name'],request.vars['mac'],request.vars['macWlan'],request.vars['serial'],request.vars['username'],request.vars['ip'])
    response=h.process(request.vars['action'])
    l.close()
    return dict(response=response)
   
@service.json
@auth.requires_login()    
def delete():
    l=conecta()
    
    if(isinstance(request.vars['host[]'], str)):
        t = Thinclients(l,request.vars['host[]'])
        t.process("delete")
    else:
        for h in request.vars['host[]']:
            t = Thinclients(l,h)
            t.process("delete")
            
    l.close()
    return dict(response="OK")

@service.json
@auth.requires_login()
def move():
    rows = request.vars["rows"].split(",")
    l=conecta()
    if request.vars["action"]=="free_gap":
        for r in rows:
            cadena = r.split("-")
            type = cadena[1][:1]
            classroom = "a"+request.vars['classroom'].zfill(2)
            newName = Thinclients(l).findFreeGaps(classroom,type,request.vars['startIN'])["freeGaps"][0]

            Thinclients(l,r).move(newName)
            
    elif request.vars["action"]=="overwrite":
        num_computer = int(request.vars['startIN'])
        for r in rows:
            cadena = r.split("-")
            type = cadena[1][:1]
            classroom = "a"+request.vars['classroom'].zfill(2)
            computer = type+str(num_computer).zfill(2)
            newName = classroom+"-"+computer

            if r!=newName:				
				if request.vars['backup']=="no":
					Thinclients(l,newName).delete() # Borrar el destino para abrir hueco
				else:
					backup = Thinclients(l).findFreeGaps("a9999",type,1)["freeGaps"][0]
					Thinclients(l,newName).move(backup)

				Thinclients(l,r).move(newName) # Mover el equipo a su nuevo destino

				num_computer = num_computer+1
            
    l.close()
    return dict(response="OK")

@service.json
@auth.requires_login()
def removeAssigns():
    l=conecta()
    
    if(isinstance(request.vars['host[]'], str)):
        t = Thinclients(l,request.vars['host[]'])
        t.modifyUser()
    else:
        for h in request.vars['host[]']:
            t = Thinclients(l,h)
            t.modifyUser()
            
    l.close()
    return dict(response="OK")

@service.json
@auth.requires_login()
def getNodes():
    l=conecta()
    t = Thinclients(l)
    groups = t.getThinclientGroups()

    response=[]
    for g in groups["groups"]:
        if (not "-wifi" in g) and (not "group" in g):
            response.append(g)
    return dict(response=sorted(response))

@service.json
@auth.requires_login()
def getComputersNode():
    l=conecta()
    t = Thinclients(l)
    computers = t.getAllComputersNode(request.vars['node'])
    return dict(response=sorted(computers["computers"]))

@service.json  
@auth.requires_login()    
def getUsers():
    l=conecta()
    g = Groups(l,"",request.vars['name'],"")
    response = g.getGroupUsersData()
    l.close()
    return dict(response=response)  

@service.json
@auth.requires_login()
def saveAssignation():
    l=conecta()
    j=0
    for i in request.vars['computers[]']:
        try:
            t = Thinclients(l,i,username=request.vars['students[]'][j])            
            t.modifyUser();
        except:
            t = Thinclients(l,i)
            t.modifyUser();        
        j=j+1
    return dict(response="OK")

@service.json
@auth.requires_login()
def setIP():
    try:
        if (isinstance(request.vars["nodes[]"],str)):
            nodes = [request.vars["nodes[]"]]
        else:
            nodes = request.vars["nodes[]"]          
    except:
        nodes = "None"

    if not nodes:
        return dict(response="no_groups_selected")

    l=conecta()
    for n in nodes:
        c = Thinclients(l).getAllComputersNode(n)
        computers = sorted(c["computers"])
        ip = request.vars["ip"]
        for i in computers:
            new_ip = "192.168.0."+str(ip)
            if new_ip!="192.168.0.254":
            	t = Thinclients(l,i,ip=new_ip)
            	t.modifyIP()

            ip = int(ip)+1

    return dict(response="OK")

@auth.requires_login()
def addHistory(l,username,id_laptop,computer_name):
    
    lh = LaptopsHistory(cdb,"",id_laptop,"","","","","","","")
    lastUsername = lh.getLastHistory()

    if username!="" and lastUsername['username']!=username:
        u = Users(l,"","","","",username,"","","","")
        userData = u.getUserData()
        
        if userData["uidnumber"]!="": # Si existe el usuario
            lh.set_id_state(2) # Asignado
            
            if userData["type"]=="student":
                lh.set_id_user_type(2)
            elif userData["type"]=="teacher":
                lh.set_id_user_type(1)

            lh.set_computer_name(computer_name)    
            lh.set_username(username)
            lh.set_name(userData["name"]+" "+userData["surname"])
            lh.set_nif(userData["nif"])
            lh.set_comment("Volcado masivo ControlIES")
            lh.add()
    
    elif username=="" and lastUsername['username']!="":
        lh.set_id_state(1) # No Asignado
        lh.set_computer_name(computer_name)        
        lh.set_comment("Volcado masivo ControlIES")
        lh.add()

@service.json
@auth.requires_login()
def databaseDumpExec():
    
    try:
        if request.vars['massive_desasignation']=="ok":
            # Get all students asigned laptops
            sql="SELECT id_laptop FROM laptops_historical lh"
            sql=sql+" WHERE lh.id_state=2 AND lh.id_user_type=2"
            sql=sql+" AND lh.id_historical IN (SELECT MAX(lh2.id_historical) FROM laptops_historical lh2 WHERE lh2.id_laptop=lh.id_laptop)"
            sql=sql+" GROUP BY id_laptop"
            sql=sql+" ORDER BY id_laptop"
            result = cdb.executesql(sql)

            for r in result:
                lh = LaptopsHistory(cdb,"",r[0],1,"","","","","Desasignación masiva ControlIES","")
                lh.add()
    except:
        pass

    l=conecta()
    t = Thinclients(l)
    result = t.getAllComputers()

    for c in result["computers"]:
        
        computer_name = c["cn"].strip()
        serial = c["serial"].replace("serial-number","").strip()
        username = c["username"].replace("user-name","").strip()
        mac = c["mac"].replace("ethernet","").strip()
        macWlan = c["macWlan"].replace("ethernet","").strip()

        if serial!="":        
            id_laptop = Laptops(cdb,"","","","","","","","").existsSerialNumber(serial)
            if id_laptop:
                addHistory(l,username,id_laptop,computer_name)

                lap = Laptops(cdb,id_laptop,"","","","","","","")
                laptop = lap.getLaptopData()
                if laptop["mac_eth0"]!=mac or laptop["mac_wlan0"]!=macWlan:
                    lap.updateMAC(mac,macWlan)

            else: # Si no existe el portatil
                try:
                    if request.vars['add_laptop']=="ok":  
                        lap = Laptops(cdb,"", serial, "", "", "", "", mac, macWlan)
                        lap.add()
                        
                        addHistory(l,username,lap.getIdLaptop(),computer_name)
                except:
                    pass

    l.close()

    return dict(response = "OK")   

@service.json
@auth.requires_login()
def findDuplicates():
    l=conecta()
    t = Thinclients(l)
    result = t.getAllComputers()
    
    serials = []
    macs = []
    users = []
        
    for c in result["computers"]:
        try:
            serial = c["serial"].replace("serial-number","").strip()
            if serial!="":
                serials.append(serial)
        except:
            pass

        try:
            mac = c["mac"].replace("ethernet","").strip()
            if mac!="":
                macs.append(mac)
        except:
            pass

        try:
            user = c["username"].replace("user-name","").strip()
            if user!="":
                users.append(user)
        except:
            pass

    s = set([x for x in serials if serials.count(x) > 1])
    m = set([x for x in macs if macs.count(x) > 1])
    u = set([x for x in users if users.count(x) > 1])
        
    return dict({"users":sorted(u), "macs":sorted(m), "serials":sorted(s)})

#necesaria estas funciones en el controlador para poder cargar las vistas correspondientes:    

def findDuplicate():
    return dict()

def databaseDump():
    return dict()

def form():
    return dict()

def form_move():
    return dict()

def assignComputers():
    return dict()

def assignIP():
    return dict()
  
def call():
    session.forget()
    return service()
