import asyncio
import logging
import threading

import netifaces as ni
import socket
import os
import json
import socketio
import asyncio
from datetime import datetime
from enum import Enum

from netifaces import interfaces, ifaddresses, AF_INET

from .Server import Server, CommandResult
from .AsyncService import AsyncService, StatusEnum
from .InterfaceService import InterfaceService, events as InterfaceEvents
from ..helpers.ApiResponse import ApiResponse, ReponseTypes

class CommunicationService(AsyncService):

    instance = None

    @staticmethod
    def getInstance():
        if CommunicationService.instance is not None:
            return CommunicationService.instance
        else:
            return None

    @staticmethod
    def createInstance():
        if CommunicationService.instance is not None:
            return CommunicationService.instance
        else:
            CommunicationService.instance = CommunicationService()
    def __init__(self):
        super().__init__()
        self.name = "CommunicationService"
        self.knownServers = []
        self.current_server = None
        self.is_connected = False
        self.url = None
        self.connection_status = ConnectionStates.DISCONNECTED
        self.tasks = set()
        self.loop = None
        self.socket = None
        CommunicationService.instance = self

    async def initFunc(self, *args):
        print("Initializing Communication Service")
        # Find available network interfaces
        self.network_addresses = self.find_network_interfaces()

        # If an external address is available, use it. Otherwise, use internal
        if not self.network_addresses["external"]:
            self.select_network_interface(self.network_addresses["internal"][0])
        else:
            self.select_network_interface(self.network_addresses["external"][0])
            print("Using network interface: " + self.url)

        # Load last known server from localStorage
        try:
            db_server_object = self.settingsService.loadServer()
            servers = [db_server_object] if db_server_object is not None else []

            if not servers or len(servers) == 0:
                # No recent servers found
                self.connection_status = ConnectionStates.READYTOCONNECT
            else:
                # Server entries found.
                # Sort by last Connection and try the most recent one
                try:
                    servers.sort(key=lambda s: s.lastConnection , reverse=True)
                except:
                    print("Failed to sort servers by last Connection")
                # Create rt objects
                rt_servers = [Server(db_server, self.url, self.loop) for db_server in servers]
                self.knownServers = rt_servers

                # Try to connect to the most recent one
                self.current_server = Server.load_from_storage(servers[0], self.url, self.loop)

                try:

                    self.socket = await self.current_server.tcp_connect()
                    # Connection successful
                    self.connection_status = ConnectionStates.CONNECTED
                    # await self.socket.wait()
                    # add listeners in different thread
                    # await self.current_server.socket_add_listeners()
                    # self.socket.start_background_task(self.socket.wait())
                    async def connect():
                        self.socket = await self.current_server.tcp_connect()
                        # Connection successful
                        self.connection_status = ConnectionStates.CONNECTED
                        # add listeners in different thread
                        # await self.current_server.socket_add_listeners()
                        # await self.socket.wait()
                    def thread_runner():
                        loop = asyncio.get_event_loop()
                        asyncio.set_event_loop(loop)
                        task = loop.create_task(connect())
                        self.tasks.add(task)
                        # loop.run_forever()
                        loop.run_until_complete(task)
                        # loop.close()
                    # t = threading.Thread(target=thread_runner, args=[])
                    # t.start()
                except Exception as err:
                    # Connection error
                    print("Failed to connect to last known server. Reason: " + str(err))
                    print("State is now: " + ConnectionStates.READYTOCONNECT.value)
                    self.connection_status = ConnectionStates.READYTOCONNECT


            return
        except Exception as err:
            print("Failed to connect to last known server. Reason: " + str(err))
            print("State is now: " + ConnectionStates.READYTOCONNECT.value)
            self.connection_status = ConnectionStates.READYTOCONNECT
            return

    async def start(self, *args):
        self.debug("Starting Service: " + self.name)
        if self.status == StatusEnum.RUNNING:
            return True
        self.initStarted = True
        self.systemSettings = self.settingsService.getSettings()
        # def thread_runner():
        #     loop = asyncio.new_event_loop()
        #     # asyncio.set_event_loop(loop)
        #     self.loop = loop
        #     task = loop.create_task(self.initFunc(args))
        #     self.tasks.add(task)
        #     loop.run_until_complete(task)
        try:
            self.status = StatusEnum.RUNNING
            await self.initFunc(args)
            return True
        except Exception as e:
            self.status = StatusEnum.FAILED
            self.debug("ERROR: Service startup failed: " + self.name)
            logging.error("ERROR: Service failed to start: " + self.name)
            return False



        
    def get_ip_address(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]

    async def handle_tcp_connection_request(self, server_information):
        server_id = server_information['serverId']
        url = server_information['url']
        endpoints = server_information['endpoints']

        if self.connection_status == ConnectionStates.READYTOCONNECT:
            # Decide whether to register or connect
            known_host = next((server for server in self.knownServers if server.serverId == server_id), None)

            if known_host:
                # Update server endpoints
                known_host.endpoints = endpoints
                self.current_server = known_host

                try:
                    await self.current_server.tcp_connect()
                    self.connection_status = ConnectionStates.CONNECTED
                    response = {
                        'server': self.current_server,
                        'state': self.connection_status,
                        'result': ApiResponse(ReponseTypes.REGISTRATION.ALREADYREGISTERED)
                    }
                    return response
                except Exception as tcp_error:
                    err_data = tcp_error.data
                    response = {
                        'server': self.current_server,
                        'state': self.connection_status,
                        'result': ApiResponse(ReponseTypes.REGISTRATION.FAILED),
                        'error': tcp_error
                    }

                    if err_data['code'] == 1:
                        # Connection error
                        response['result'] = ApiResponse(ReponseTypes.CONNECTION.FAILED)
                    elif err_data['code'] == 23:
                        response['result'] = ApiResponse(ReponseTypes.REGISTRATION.EXPIRED)
                        try:
                            result = await self.current_server.tcp_register()
                            self.current_server.server_id = result.serverId
                            self.current_server.client_id = result.clientId
                            self.settingsService.saveServer(self.current_server)
                            await self.current_server.tcp_connect()
                            self.connection_status = ConnectionStates.CONNECTED
                            response['result'] = ApiResponse(ReponseTypes.REGISTRATION.RENEWED)
                        except Exception as tcp_error:
                            response['error'] = tcp_error
                            return response
                    else:
                        return response
            else:
                # Register
                self.current_server = Server(server_information, self.url, self.loop)

                try:
                    result = await self.current_server.tcp_register()
                    self.current_server.server_id = result.server_id
                    self.current_server.client_id = result.client_id
                    self.settingsService.saveServer(self.current_server)
                    await self.current_server.tcp_connect()
                    self.connection_status = ConnectionStates.CONNECTED
                    response = {
                        'server': self.current_server,
                        'state': self.connection_status,
                        'result': ApiResponse(ReponseTypes.REGISTRATION.SUCCESSFUL)
                    }
                    return response
                except Exception as err:
                    return {'error': err}
        else:
            # Check if already connected to this server
            if self.current_server.server_id == server_id:
                # Already connected
                response = {
                    'server': self.current_server,
                    'state': self.connection_status,
                    'result': ApiResponse(ReponseTypes.REGISTRATION.ALREADYREGISTERED)
                }
                return response
            else:
                # Connection refused
                raise Exception("Connection refused.")

    def send_command_callback(self, command, cb):

        if self.connection_status is not ConnectionStates.CONNECTED:
            print("Unable to send command: not connected.")
        def callback_wrapper(result):
            cb(result)

        async def run_async():
            try:
                # return True
                result = await self.current_server.tcp_send_command(command)
                # result.result contains ["success", "failed"]
                # result.response contains server response
                callback_wrapper(result)

            except Exception as e:
                # Failed to send command
                print("Failed to send command to server.")
                raise e

        loop = asyncio.get_event_loop()
        t = loop.create_task(run_async())
        self.tasks.add(t)
        loop.run_until_complete(t)

    async def send_command(self, command):
        try:
            # return True
            result = await self.current_server.tcp_send_command(command)
            await result
            # result.result contains ["success", "failed"]
            # result.response contains server response
            return result.result()
    
        except Exception as e:
            # Failed to send command
            print("Failed to send command to server.")
            raise e

    def find_network_interfaces(self):
        results = {
            'internal': [],
            'external': []
        }

        ip_list = []
        available_ifs = interfaces()
        for interface in available_ifs:
            if AF_INET in ifaddresses(interface):
                for link in ifaddresses(interface)[AF_INET]:
                    results["internal"].append({"name": interface, "address": link, "internal": True})

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        results["external"].append({"name": "external", "address": s.getsockname()[0], "internal": False})
        s.close()
        return results

    def select_network_interface(self, entry, protocol="http://"):
        if not entry.get('address'):
            if isinstance(entry, str):
                entry = {'address': entry}
        self.url = protocol + entry['address']
        return self.url


class ConnectionStates(Enum):
    CONNECTED = 'connected'
    DISCONNECTED= 'disconnected'
    READYTOCONNECT= 'readyToConnect'
    DISABLED = 'disabled'