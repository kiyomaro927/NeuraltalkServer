from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import os
import logging
import cgi
import cv2
import commands
import re

class HTTPRequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        response_body = 'I got an illegal access.\n'
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
            response_body = "no file given\n"
        else:
            # save image file to target directry.
            item = form["file"]
            if item.file:
                fout = file(os.path.join('./target/', item.filename), 'wb')
                buffersize = 1000000
                while True:
                    chunk = item.file.read(buffersize)
                    if not chunk:
                        break
                    fout.write(chunk)
                    fout.close()

            # execute neuraltalk
            neuraltalk = commands.getoutput("th eval.lua -model /home/kiyomaru/model_id1-501-1448236541.t7_cpu.t7 -image_folder ./target/ -num_images 1 -gpuid -1")

            # extract result
            pattern = "\[.+?\]"
            response_body = re.search(pattern, neuraltalk).group(0)[1:-1]
            
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


# Start the server.
script_dir = './log'
logging.basicConfig(filename=script_dir + '/server.log', format='%(asctime)s %(message)s', level=logging.DEBUG)

host = 'localhost'
port = 8000
httpd = HTTPServer((host, port), HTTPRequestHandler)

logging.info('Server Starting...')
logging.info('Listening at port :%d', port)

try:
    httpd.serve_forever()
except:
    logging.info('Server Stopped')