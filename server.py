#  coding: utf-8 
import SocketServer
import os
import mimetypes

# Copyright 2013 Abram Hindle, Eddie Antonio Santos
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(SocketServer.BaseRequestHandler):
    
    base_URL = "http://127.0.0.1:8080/"    
    
    def check_available_pages(self, path, base_directory):
        files_in_directory = ['/']
        for root, dirs, files in os.walk(base_directory, topdown=False):
            for name in files:
                if(name[0] != "."):
                    files_in_directory.append(root[5:]+"/"+name)
        return path in files_in_directory

    def build_content_line(self, mimetype):
        content_line = ""
        if (mimetype != None):
            content_line = "content-type: " + mimetype + "; charset=utf-8"
        return content_line

    def send_ok_response(self, path):
        file_type = mimetypes.guess_type(path)[0]
        index = "index.html"
        if (file_type == None and self.check_available_pages(index,"."+ path)):
            file = open(path+index,'r')
            self.request.sendall(self.build_response_header(200,"Found", self.build_content_line(file_type)))
            self.request.sendall(file.read())
        else:
            self.request.sendall(self.build_response_header(200, "Not Found", self.build_content_line(file_type)))

    def build_response_header(self, status_code, message, content_type_line):
        if(content_type_line != ""):
            content_type_line = "\r\n" + content_type_line
        return "HTTP/1.1 " + str(status_code) + " "+ message + content_type_line + "\r\n\r\n"

    def parse_request(self,data):
        divided_data = self.data.split()
        http_method = divided_data[0]
        path = divided_data[1]
        http_protocol = divided_data[2]
        requester = divided_data[4]
        host = divided_data[6]
        accept = divided_data[8]
        # Check path to make sure there are no preceeding dots
        if self.check_available_pages(path, "./www"):
             self.send_ok_response(path)              
        else:
            header = self.build_response_header(404, "Not Found", "")
            self.request.sendall(header)
    
    def handle(self):
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)
        self.parse_request(self.data)



if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    SocketServer.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = SocketServer.TCPServer((HOST, PORT), MyWebServer)
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
