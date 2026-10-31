import unittest
from progress_ui import preview_url
from research import choose_start

class ProgressTests(unittest.TestCase):
 def test_preview_domains_and_unsafe_urls(self):
  good=['https://tf-test.fra0-tinyfish.unikraft.app/stream/0',
        'https://ip-test.tetra-data.production.tinyfish.io/stream/0']
  for url in good:self.assertEqual(preview_url(url),url)
  for url in ['javascript:alert(1)','http://localhost:9000','https://tinyfish.io.evil.example/a',
              'https://user:password@agent.tinyfish.ai/a','https://unrelated.unikraft.app/a']:
   self.assertIsNone(preview_url(url))
 def test_discovery_never_uses_a_rental(self):
  rows=[{'url':'https://housing.com/rent/123','title':'2 BHK rent'},
        {'url':'https://housing.com/in/buy/bengaluru/electronic-city-gid/2bhk-flats-fid/','title':'2 BHK sale'}]
  self.assertEqual(choose_start(rows,2),rows[1]['url'])
