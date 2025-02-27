import aiohttp
from aiohttp import BasicAuth
import logging
from urllib.parse import urljoin
import time
import async_timeout

_LOGGER = logging.getLogger(__name__)

class PanasonicCamera:
    """Class to handle Panasonic Camera I/O operations."""

    TERMINAL_TYPES = {
        1: {
            'name': 'Terminal 1',
            'modes': ['alarm_input', 'aux_input'],
            'default': 'alarm_input',
            'states': {
                'high': 'ON',  # Changed to match HA states
                'none': 'OFF',
                'unknown': 'UNKNOWN'
            }
        },
        2: {
            'name': 'Terminal 2',
            'modes': ['alarm_input', 'alarm_output'],
            'default': 'alarm_output',
            'states': {
                'high': 'ON',
                'none': 'OFF',
                'unknown': 'UNKNOWN'
            }
        },
        3: {
            'name': 'Terminal 3',
            'modes': ['alarm_input', 'aux_output'],
            'default': 'aux_output',
            'states': {
                'high': 'ON',
                'none': 'OFF',
                'unknown': 'UNKNOWN'
            }
        }
    }

    IO_CONFIG = {
        'input': {
            'endpoint': '/cgi-bin/get_io',
            'high_state': 'high',
            'low_state': 'none'
        },
        'output': {
            'endpoint': '/cgi-bin/get_io',
            'aux_control': {
                'endpoint': '/cgi-bin/terminal_set',
                'params': {
                    'ON': {'state': '1'},
                    'OFF': {'state': '0'}
                }
            }
        }
    }

    def __init__(self, ip, port=80, username='admin', password='12345'):
        """Initialize camera connection."""
        self.base_url = f"http://{ip}:{port}"
        self.terminal_states = {}
        self.username = 'Admin' if not username or username.lower() == 'admin' else username
        self.password = password
        self.ip = ip
        
        self.headers = {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Connection': 'keep-alive',
            'Host': ip,
            'Cache-Control': 'no-cache'
        }
        
        self._output_states = {2: False, 3: False}
        self.terminal_configs = {}
        self._initialize_terminals()

    async def _test_connection(self):
        """Test camera connection."""
        try:
            return await self._make_request('/cgi-bin/get_io') is not None
        except Exception as e:
            _LOGGER.error(f"Connection test failed: {str(e)}")
            return False

    async def _make_request(self, endpoint, method='GET', params=None):
        """Make HTTP request with error handling."""
        url = urljoin(self.base_url, endpoint)
        try:
            all_params = {'Language': '0', **(params or {})}
            auth = BasicAuth(self.username, self.password)

            async with async_timeout.timeout(10):
                async with aiohttp.ClientSession(auth=auth) as session:
                    async with session.request(
                        method,
                        url,
                        params=all_params if method == 'GET' else None,
                        data=all_params if method != 'GET' else None,
                        headers=self.headers,
                        ssl=False
                    ) as response:
                        if response.status == 401:
                            _LOGGER.error("Authentication failed")
                            return None
                        
                        return await response.text()
                    
        except Exception as e:
            _LOGGER.error(f"Request failed: {str(e)}")
            return None

    async def get_io_status(self):
        """Get status of all I/O terminals."""
        response = await self._make_request('/cgi-bin/get_io')
        if response:
            return self._parse_io_status(response)
        return None

    def _parse_io_status(self, status_text):
        """Parse I/O status response."""
        states = {}
        for line in status_text.split('\n'):
            if 'terminal' in line.lower():
                parts = line.split(':')
                if len(parts) == 2:
                    terminal = int(parts[0].split()[1])
                    state = parts[1].strip().lower()
                    
                    states[terminal] = {
                        'state': 'ON' if state == self.IO_CONFIG['input']['high_state'] else 'OFF',
                        'raw_state': state
                    }
        return states

    async def set_output(self, terminal, state):
        """Control terminal output state."""
        if terminal not in [2, 3]:
            raise ValueError("Only terminals 2 and 3 can be outputs")
            
        params = {
            'state': '1' if state else '0',
            'terminal': str(terminal)
        }
        
        response = await self._make_request(
            self.IO_CONFIG['output']['aux_control']['endpoint'],
            params=params
        )
        
        success = response is not None
        if success:
            self._output_states[terminal] = state
            _LOGGER.info(f"Set terminal {terminal} to {'ON' if state else 'OFF'}")
        
        return success

    def _initialize_terminals(self):
        """Set up initial terminal configurations."""
        for terminal, config in self.TERMINAL_TYPES.items():
            self.terminal_configs[terminal] = {
                'mode': config['default'],
                'state': 'OFF'
            }
