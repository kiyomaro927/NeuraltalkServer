from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import os
import logging
import cgi
import re
import sys
import signal
import commands
import argparse
import subprocess


pid = -1 #neuraltalk server's process id

# signal handling
def handler(num, p):
    print 'killing subprocess...'
    if pid > 0:
        cmd = 'ps a | grep eval.lua'
        subprocess = commands.getoutput(cmd).split("\n")
        for p in subprocess:
            os.kill(int(p.split(" ")[0]), signal.SIGINT)
    exit(0)

class HTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        response_body = 'Get Request is not available.\n'
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=UTF-8')
        self.send_header('Content-length', len(response_body))
        self.end_headers()
        self.wfile.write(response_body)
        logging.info('[Request method] GET')
        logging.info('[Request headers]\n' + str(self.headers))

    def do_POST(self):
        form = cgi.FieldStorage(
            fp = self.rfile,
            headers = self.headers,
            environ = {'REQUEST_METHOD':'POST',
                       'CONTENT_TYPE':self.headers['Content-Type'],
                   })
        
        if not form.has_key("file"):
            response_body = "Give image file with -file option.\n"
        else:
            #clean up target directry
            target_dir = "./target/"
            file_list = os.listdir(target_dir)
            for filename in file_list:
                try:
                    if os.path.isfile(os.path.join(target_dir, filename)) and filename != '.gitkeep':
                        os.remove(os.path.join(target_dir, filename))
                except:
                    pass
            # save image file to target directry.
            item = form["file"]
            if item.file:
                fout = file(os.path.join('./target', item.filename), 'wb')
                while True:
                    chunk = item.file.read(1000000)
                    if not chunk:
                        break
                    fout.write(chunk)
                    fout.close()

            cmd = ('curl localhost:8888')
            caption = commands.getoutput(cmd).split("\n")[3] #avoid header
            response_body = caption


        self.send_response(200)
        self.send_header('Content-type', 'text/xml; charset=UTF-8')
        self.send_header('Content-length', len(response_body))
        self.end_headers()
        self.wfile.write(response_body)
        logging.info('[Request method] POST')
        logging.info('[Request headers]\n' + str(self.headers))

        content_len = int(self.headers.getheader('content-length', 0))
        post_body = self.rfile.read(content_len)
        logging.info('[Request doby]\n' + post_body)

def main():
    # Global variables
    global pid
    
    # Local variables
    parser = argparse.ArgumentParser()
    parser.add_argument('-host', action='store',dest='hostip',default='localhost')
    parser.add_argument('-gpuid', action='store', dest='id', default=1, type=int)

    # Set signal handler
    signal.signal(signal.SIGINT, handler)

    # Start neuraltalk server
    cmd = "th eval.lua -model ./model/model* -image_folder ./target/ -num_images 1"
    if parser.parse_args().id == -1:
        cmd += " -gpuid -1"

    p = subprocess.Popen(cmd, shell=True)
    pid = p.pid

    # Start the server.
    script_dir = './log'
    logging.basicConfig(filename=script_dir + '/server.log', format='%(asctime)s %(message)s', level=logging.DEBUG)

    host = parser.parse_args().hostip
    port = 8000
    httpd = HTTPServer((host, port), HTTPRequestHandler)
    
    print 'Server Starting...'
    logging.info('Server Starting...')
    print 'Listening at port :', port
    logging.info('Listening at port :%d', port)

    try:
        httpd.serve_forever()
    except:
        logging.info('Server Stopped')

if __name__ == '__main__':
    sys.exit(main())
