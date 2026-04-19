import logging

class Logger:
    def __init__(self,):
        logging.basicConfig(filename='cli_test.log',
                        format='%(asctime)s %(levelname)s: %(message)s',
                        filemode='a')
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

    def log_info(self, path, dst=None):
        self.logger.info(f'copied {path} to {dst}')
    
    def log_dry(self, path, dst=None):
        self.logger.info(f'Would have copied {path} to {dst}')

    def log_error(self, path, e):
        self.logger.error(f'Error copying {path}: {e}')
        
    def log_complete(self):
        self.logger.info('RUN completed successfully')

