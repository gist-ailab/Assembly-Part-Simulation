import socket
from enum import Enum

from script.const import SocketType, FreeCADRequestType, PyRepRequestType, InstructionRequestType
from script.socket_utils import *
from script.fileApi import *
import random
import time
from sequence_example import *
from pyprnt import prnt

class SocketModule():
    def __init__(self):
        self.c_freecad = self.initialize_freecad_client()
        self.c_pyrep = self.initialize_pyrep_client()
        self.c_instruction = self.initialize_instruction_client()

    def initialize_freecad_client(self):
        host = SocketType.freecad.value["host"]
        port = SocketType.freecad.value["port"]
        sock = socket.socket()
        sock.connect((host, port))
        print("==> Connected to FreeCAD server on {}:{}".format(host, port))
        
        return sock

    def initialize_pyrep_client(self):
        host = SocketType.pyrep.value["host"]
        port = SocketType.pyrep.value["port"]
        sock = socket.socket()
        sock.connect((host, port))
        print("==> Connected to PyRep server on {}:{}".format(host, port))
        
        return sock

    def initialize_instruction_client(self):
        host = SocketType.instruction.value["host"]
        port = SocketType.instruction.value["port"]
        sock = socket.socket()
        sock.connect((host, port))
        print("==> Connected to Instruction server on {}:{}".format(host, port))
        
        return sock

    #region freecad module
    def initialize_cad_info(self, cad_file_path):
        """
        """
        request = FreeCADRequestType.initialize_cad_info
        print("Request {} to FreeCAD Module".format(request))
        sendall_pickle(self.c_freecad, request)
        response = recvall_pickle(self.c_freecad)
        while not response:
            response = recvall_pickle(self.c_freecad)
        # send cad file path and get part info
        request = cad_file_path
        sendall_pickle(self.c_freecad, request)
        print("...Waiting for part info from FreeCAD Module")
        part_info = recvall_pickle(self.c_freecad)
        print("Get Part info from FreeCAD Module")

        return part_info

    def check_assembly_possibility(self, assembly_info):
        request = FreeCADRequestType.check_assembly_possibility
        print("Request {} to FreeCAD Module".format(request))
        sendall_pickle(self.c_freecad, request)
        response = recvall_pickle(self.c_freecad)
        while not response:
            response = recvall_pickle(self.c_freecad)
        # send assembly_info and get true false
        request = assembly_info
        sendall_pickle(self.c_freecad, request)
        print("...Waiting for simulate assembly from FreeCAD Module")
        is_possible = recvall_pickle(self.c_freecad)
        print("is possible? {}".format(is_possible))

        return is_possible

    def extract_group_obj(self, group_status, obj_root):
        request = FreeCADRequestType.extract_group_obj
        print("Request {} to FreeCAD Module".format(request))
        sendall_pickle(self.c_freecad, request)
        response = recvall_pickle(self.c_freecad)
        while not response:
            response = recvall_pickle(self.c_freecad)
        # send assembly_info and get true false
        request = {
            "group_status": group_status,
            "obj_root": obj_root
        }
        sendall_pickle(self.c_freecad, request)
        print("...Waiting for export group obj")
        success_to_export = recvall_pickle(self.c_freecad)
        print("{} to export obj".format(success_to_export))

    #endregion
    
    #region pyrep module
    #endregion

    #region instruction module
    def get_instruction_info(self, group_info):
        request = InstructionRequestType.get_instruction_info
        print("Request {} to Instruction Module".format(request))
        sendall_pickle(self.c_instruction, request)
        response = recvall_pickle(self.c_instruction)
        assert response, "Not ready to get instruction info"
        # send group_info and get instruction info
        request = group_info
        sendall_pickle(self.c_instruction, request)
        print("...Waiting for instruction info")
        instruction_info = recvall_pickle(self.c_instruction)
        print("Instruction info is")
        prnt(instruction_info)
    #endregion



    def close(self):
        self.c_freecad.close()
        self.c_pyrep.close()
        self.c_instruction.close()

if __name__=="__main__":
    s = SocketModule()
    # part_info = s.initialize_cad_info("./cad_file/STEFAN")
    # save_dic_to_yaml(part_info, "./assembly/STEFAN/part_info.yaml")
    """
    # TODO: create part instance info
    
    part_instance_info = {}
    instance_group_status = {}
    for part_name in part_info.keys():
        part_instance_info[part_name] = {}
        try:
            quantity = part_instance_quantity[part_name]
        except:
            quantity = 1
        for i in range(quantity):
            part_instance_info[part_name][i] = {
                "used_assembly_points": [],
                "instance_group_id": 0
            }
    save_dic_to_yaml(part_instance_info, "./part_instance_info.yaml")
    instance_group_status[0] = []
    """
    """
    part_instance_info = load_yaml_to_dic("./part_instance_info_sequence_2.yaml")
    instance_group_status = load_yaml_to_dic("./instance_group_status_sequence_2.yaml")
    for instruction_info in sequence_3:
        part_0 = instruction_info[0]["part_name"]
        instance_id_0 = instruction_info[0]["instance_id"]
        point_idx_0 = instruction_info[0]["assembly_point"]
        instance_info_0 = part_instance_info[part_0][instance_id_0]
        instance_group_id_0 = instance_info_0["instance_group_id"]

        part_1 = instruction_info[1]["part_name"]
        instance_id_1 = instruction_info[1]["instance_id"]
        point_idx_1 = instruction_info[1]["assembly_point"]
        instance_info_1 = part_instance_info[part_1][instance_id_1]
        instance_group_id_1 = instance_info_1["instance_group_id"]

        if instance_group_id_0 == 0 and instance_group_id_1 == 0: # both primitive
            status = []
            group_id = 0
            while group_id in instance_group_status.keys():
                group_id += 1
        elif instance_group_id_0 > 0 and instance_group_id_1 > 0: # both have group
            if instance_group_id_0 == instance_group_id_1: # multi-peg-in-hole
                status = instance_group_status[instance_group_id_0]
            else:
                status = instance_group_status[instance_group_id_0] + instance_group_status[instance_group_id_1]
            group_id = instance_group_id_0
        else: # primitive + group
            group_id = max(instance_group_id_0, instance_group_id_1)
            status = instance_group_status[group_id]

        assembly_info = {
            "target":{
                0: {
                    "part_name": part_0,  # part info의 key(=part name)
                    "instance_id": instance_id_0,
                    "assembly_point": point_idx_0,
                },
                1: {
                    "part_name": part_1,
                    "instance_id": instance_id_1,
                    "assembly_point": point_idx_1,
                }
            },
            "status": status
        }
        is_possible = False
        try:
            is_possible = s.check_assembly_possibility(assembly_info)
        except:
            print("ERROR")
        if is_possible:
            instance_info_0["used_assembly_points"].append(point_idx_0)
            instance_info_1["used_assembly_points"].append(point_idx_1)
            instance_info_0["instance_group_id"] = group_id
            instance_info_1["instance_group_id"] = group_id
            instance_group_status[group_id] = assembly_info["status"] + [assembly_info["target"]]
    save_dic_to_yaml(part_instance_info, "./part_instance_info_sequence_3.yaml")
    save_dic_to_yaml(instance_group_status, "./instance_group_status_sequence_3.yaml")
    """
    
