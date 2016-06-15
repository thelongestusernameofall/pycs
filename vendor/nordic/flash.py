#-----------------------------------------------------------------------------
"""
Flash Driver for Nordic Chips

Notes:

1) Instantiating this driver does not touch the hardware. No reads or writes.
We only access the hardware when the user wants to do something.

2) The SVD file has the UICR region as 4KiB in size. On the chip I've looked
at the actual flash storage is 1KiB, but we maintain the lie. It's not
harmful- just be aware that you may not be able to use the whole region for
storage.

3) The UICR regions is not completely erasable/writeable. If you erase it
certain Nordic reserved locations don't get erased. I suppose we are limited to
locations marked as "customer reserved" in the SVD.

4) According to the datasheet we can't write a code0 region from the SWD debug
interface. So - we don't bother with code 0 regions. I don't have one in this
chip in any case (FICR.CLENR0 = 0xffffffff).

5) Checking for sane inputs is a common problem and is done in common code.
The general assumption for the driver API is that inputs have been checked
and the driver can just get on with the job. ie - dealing with the hardware.

"""
#-----------------------------------------------------------------------------

import time

import util
import mem

#-----------------------------------------------------------------------------

# NVMC.CONFIG bits
CONFIG_REN = 0 # read enable
CONFIG_WEN = 1 # write enable
CONFIG_EEN = 2 # erase enable

#-----------------------------------------------------------------------------

class flash(object):

  def __init__(self, device):
    self.device = device
    self.io = self.device.NVMC
    self.init = False

  def __flash1_pages(self):
    """return a list of pages for the flash code 1 region"""
    adr = self.device.flash1.address
    number_of_pages = self.device.flash1.size / self.page_size
    return [mem.region('flash1', adr + (i * self.page_size), self.page_size) for i in range(number_of_pages)]

  def __uicr_pages(self):
    """return a list of pages for the UICR region"""
    adr = self.device.UICR.address
    number_of_pages = self.device.UICR.size / self.page_size
    return [mem.region('UICR', adr + (i * self.page_size), self.page_size) for i in range(number_of_pages)]

  def __hw_init(self):
    """initialise the hardware"""
    if self.init:
      return
    # build a list of flash pages
    #self.number_of_pages = self.device.FICR.CODESIZE.rd()
    self.page_size = self.device.FICR.CODEPAGESIZE.rd()
    self.pages = []
    self.pages.extend(self.__flash1_pages())
    self.pages.extend(self.__uicr_pages())
    # build some memory regions to represent the flash memory
    self.code1 = mem.region(None, self.device.flash1.address, self.device.flash1.size)
    self.uicr = mem.region(None, self.device.UICR.address, self.device.UICR.size)
    self.init = True

  def __wait4ready(self):
    """wait for flash operation completion"""
    for i in xrange(5):
      if self.io.READY.rd() & 1:
        # operation completed
        return
      time.sleep(0.1)
    assert False, 'time out waiting for flash ready'

  def sector_list(self):
    """return a list of flash pages"""
    self.__hw_init()
    return self.pages

  def in_flash(self, x):
    """return True if x is contained within a flash region"""
    self.__hw_init()
    if self.code1.contains(x):
      return True
    if self.uicr.contains(x):
      return True
    return False

  def erase(self, p):
    """erase a flash page - return non-zero for an error"""
    self.__hw_init()
    self.__wait4ready()
    self.io.CONFIG.wr(CONFIG_EEN)
    if p.name == 'flash1':
      self.io.ERASEPCR1.wr(p.adr)
    elif p.name == 'UICR':
      self.io.ERASEUICR.wr(p.adr)
    else:
      assert False, 'unrecognised flash page name %s' % p.name
    self.__wait4ready()
    self.io.CONFIG.wr(CONFIG_REN)
    return 0

  def wrbuf(self, adr, buf):
    """write a buffer of 32 bit words to the 32 bit aligned memory adr"""
    self.__wait4ready()
    self.io.CONFIG.wr(CONFIG_WEN)
    self.device.cpu.wr_buf(adr, buf)
    self.__wait4ready()
    self.io.CONFIG.wr(CONFIG_REN)

  def __str__(self):
    self.__hw_init()
    return util.display_cols([x.col_str() for x in self.pages])

#-----------------------------------------------------------------------------