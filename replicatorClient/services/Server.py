import asyncio
import logging
import netifaces as ni
import socket
import os
import json
import socketio
import asyncio
import nest_asyncio

from replicatorClient.helpers.TcpResponseGenerator import tcp_response_generator

nest_asyncio.apply()
import aiohttp
from datetime import datetime
from replicatorClient.services.InterfaceService import InterfaceService
from replicatorClient.services.SettingsService import SettingsService
from replicatorClient.services.ServerCommandService import ServerCommandService


class Server:
    @staticmethod
    def load_from_storage(obj, url, loop):
        return Server(obj, url, loop)

    def __init__(self, db_server_object, client_url="", loop=None):
        self.identifier = db_server_object.get('identifier', None)
        self.server_id = db_server_object.get('serverId',None)
        self.endpoints = db_server_object.get('endpoints', None)
        self.url = db_server_object.get('url',None)
        self.own_url = db_server_object.get('ownUrl', None)
        self.client_id = db_server_object.get('clientId', None)
        self.last_connection = db_server_object.get('lastConnection', None)
        self.created_date = db_server_object.get('createdDate', None)
        self.client_url = client_url

        self.settingsService = SettingsService.getInstance()
        self.settings = self.settingsService.getSettings()

        self.endpoint_url = f"http://{self.endpoints['tcp']['address']}:{self.endpoints['tcp']['port']}"
        self.registration_endpoint = self.endpoint_url
        self.tasks = set()
        self.socket = None
        self.connected = False

    def to_json(self):
        return {
            'identifier': self.identifier,
            'serverId': self.server_id,
            'endpoints': self.endpoints,
            'url': self.url,
            'ownUrl': self.own_url,
            'clientId': self.client_id,
            'lastConnection': self.last_connection,
            'createdDate': self.created_date,
            'connected': self.connected,
        }

    async def test(self):
        try:
            response = await self.send({'path': '/hello'})
            if response['ok']:
                return response
            raise Exception(response)
        except Exception as err:
            raise err

    async def tcp_connect(self):

        if self.socket is not None:
            if self.socket.connected:
                return self.socket
            else:
                # await self.tcp_reconnect()
                return self.socket
        else:
            socket_promise = await self.tcp_create_socket()
            # await socket_promise
            return self.socket

    async def tcp_create_socket(self, overwrite=True):
        if self.socket is not None:
            if not overwrite:
                raise Exception("Socket exists already.")

        if not self.client_id:
            raise Exception("No clientId found.")

        auth = {'clientId': self.client_id}
        socket = socketio.AsyncClient(reconnection=True, logger=True, engineio_logger=True)

        @socket.on('connect')
        async def on_connect():
            print(socket.sid)  # x8WIv7-mJelg7on_ALbx
            print("Connected to Server!")
            await socket.emit('message', 'Hello there!')
            self.connected = socket.connected
            self.last_connection = datetime.now()
            self.socket = socket
            # resolve(socket)

        @socket.on('message')
        async def on_message(data):
            print(f"Received message: {data}")

        @socket.on('settings')
        async def on_settings(data):
            settings = self.settingsService.getSettings_server_format()
            return settings

        @socket.on('interfaces')
        async def on_settings(data):
            interfaces = InterfaceService.getInstance().getAllJson()
            return interfaces

        @socket.on('updateSettings')
        async def on_settings(data):
            for key in data:
                if isinstance(data[key], dict):
                    for innerKey in data[key]:
                        self.settingsService.setKey_server_format(category=key, key=innerKey, data=data[key][innerKey])
                else:
                    self.settingsService.setKey_server_format(key=key, data=data[key])
            settings = self.settingsService.getSettings_server_format()
            return settings

        @socket.on('command')
        async def on_command(data):
            result = ServerCommandService.processCommand(data)
            return result

        @socket.on('disconnect')
        async def on_disconnect():
            print(self.socket.sid)  # undefined
            self.socket = None
            self.connected = False

        @socket.on('connect_error')
        async def on_connect_error(err):
            print("Failed to connect to server")

        @socket.on('requestClientAction')
        async def on_request_client_action(data):
            print(f"Server requested action: {data}")

        await socket.connect(self.endpoint_url, auth=auth, wait_timeout=10)

    async def tcp_reconnect(self):
        err_msg = "Failed to reconnect to socket: "
        if self.socket:
            try:
                await self.socket.connect(self.endpoint_url)
                self.connected = self.socket.connected
                return self.socket
            except Exception as err:
                print("Failed to reconnect to socket: " + str(err))
                return await self.tcp_create_socket()
        else:
            return await self.tcp_create_socket()

    async def tcp_register(self, force=False):
        err_msg = "Failed to register at server: "
        if self.client_id:
            if not force:
                print("Renewing server registration...")
            else:
                raise Exception(err_msg + "A client id is already set. Maybe you want to connect?")
        headers = {'originUrl': self.client_url}
        socket = socketio.AsyncClient(logger=True, engineio_logger=True)
        try:
            @socket.on('connect', namespace='/register')
            async def connect():
                auth_data = {
                    'identifier': self.settings["identifier"],
                    'url': self.client_url,
                    'version': self.settings["version"],
                }
                await socket.emit(event='registerClient', data=auth_data, namespace="/register")

            @socket.event(namespace='/register')
            async def disconnect():
                print("Disconnected.")
                pass  # You can handle disconnect events if needed
            @socket.on('connect_error', namespace='/register')
            async def connect_error(err):
                print("Connection error.")
                raise err

            @socket.on('registrationError', namespace='/register')
            async def on_registration_error(tcp_response):
                await socket.disconnect()
                raise Exception(err_msg + tcp_response['message'])

            @socket.on('registrationComplete', namespace='/register')
            async def on_registration_complete(tcp_response):
                if tcp_response.get('error') is not None:
                    raise Exception("Unexpected error during registration")
                print("Received tcp message: " + tcp_response.get('message', ""))
                data = tcp_response['data']
                self.server_id = data['serverId']
                self.client_id = data['clientId']
                self.client = data['client']
                await socket.disconnect()
                result = RegistrationResult(self.server_id, self.client_id, self.client, data, None, "")
                self.current_registration_result = result

            @socket.on('register', namespace='/register')
            async def on_register():
                print("We were asked to register.")

            @socket.on('*', namespace='*')
            async def any_event_any_namespace(event, namespace, sid, data):
                pass

            await socket.connect(self.registration_endpoint, headers=headers, namespaces=["/register"], wait_timeout=10)

            await socket.wait()

        except Exception as err:
            raise err

        result = self.current_registration_result
        self.current_registration_result = None
        return result

    async def api_register(self):
        err_msg = "Failed to register at server: "
        if self.client_id:
            raise Exception(err_msg + "A client id is already set. Maybe you want to connect?")
        auth_data = {'identifier': self.settings.identifier}
        try:
            response = await self.send(path='/api/v1/clients/register', method='POST', data=auth_data)
            if response.ok:
                result = await response.json()
                self.server_id = result['serverId']
                self.client_id = result['clientId']
                return result
            raise Exception(response)
        except Exception as err:
            raise err

    async def tcp_send_command(self, command):
        try:
            result = None
            socket = await self.tcp_connect()
            command_data = {'command': command.to_json(), 'clientId': self.client_id}
            main_event_loop = asyncio.get_event_loop()
            main_event_loop.run_until_complete(self.socket.emit("message", "Sending Soon!"))
            f = main_event_loop.create_future()


            def resolve(result):
                f.set_result(result)
            @socket.on('commandSuccessful')
            async def on_command_successful(response):
                nonlocal result
                result = CommandResult(response)
                resolve(result)
            @socket.on('commandFailed')
            async def on_command_failed(response):
                nonlocal result
                result = CommandResult(response)
                resolve(result)

            await socket.call(event="processCommand", data=command_data, timeout=10)
            return f

        except Exception as err:
            raise err

    def tcp_send_command_callback(self, command, cb):
        async def run_async():
            try:
                socket = await self.tcp_connect()
                command_data = {'command': command.to_json(), 'clientId': self.client_id}

                @socket.on('commandSuccessful')
                async def on_command_successful(response):
                    result = CommandResult(response)
                    cb(result)

                @socket.on('commandFailed')
                async def on_command_failed(response):
                    result = CommandResult(response)
                    cb(result)

                await self.socket.emit('processCommand', command_data)
                await socket.wait()
            except Exception as err:
                raise err
        loop = asyncio.new_event_loop()
        t = loop.create_task(run_async())
        self.tasks.add(t)
        loop.run_until_complete(t)
        loop.close()


    async def api_connect(self):
        err_msg = "Failed to authenticate at server: "
        if not self.client_id:
            raise Exception(err_msg + "No client Id set for the current server.")
        auth_data = {'identifier': self.settings.identifier, 'clientId': self.client_id}
        try:
            result = await self.send(path='/api/v1/clients/connect', method='POST', data=auth_data)
            if result.ok:
                self.last_connection = datetime.now()
                return result
            raise Exception(result)
        except Exception as err:
            raise err

    async def send(self, path='/', method='GET', data={}, options={}):
        port = f":{self.endpoints['http']['port']}" if self.endpoints['http']['port'] else ''
        url = f"http://{self.endpoints['http']['address']}{port}{path}"
        fetch_options = options
        fetch_options['method'] = method
        fetch_options['body'] = json.dumps(data)
        fetch_options['headers'] = {'Content-Type': 'application/json'}
        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, **fetch_options) as response:
                return response


class RegistrationResult:
    def __init__(self, server_id, client_id, client, data, error, message):
        self.server_id = server_id
        self.client_id = client_id
        self.client = client
        self.data = data
        self.error = error
        self.message = message

class CommandResult:
    def __init__(self, response):
        self.response = response
        result = response["result"]
        self.success = result.get("success", False)
        self.error = result.get("error", None)
        self.result = "success" if self.success else "failed"
class ServerCommandSuccessful(Exception):
    pass