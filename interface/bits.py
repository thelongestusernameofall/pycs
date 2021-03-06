#-----------------------------------------------------------------------------
"""

Bit Buffers

Notes:

1) Represents bit buffers with Python's arbitrary length integers.

2) The least signifcant bit of the internal value is transmitted first.
   That is: the transmit order is right to left (as printed)

3) The byte interface presents the bytes in transit order. ie: the least
   significant bit of byte[0] is transmitted first.

"""
#-----------------------------------------------------------------------------

import array

#-----------------------------------------------------------------------------

class bits(object):

  def __init__(self, n = 0, data = None):
    """initialise the n-bit buffer from byte values"""
    self.val = 0
    self.n = n
    if data is not None:
      for i in xrange(len(data) - 1, -1, -1):
        self.val <<= 8
        self.val |= data[i]
      self.val &= ((1 << self.n) - 1)

  def copy(self):
    """return a copy of the bit buffer"""
    x = bits()
    x.n = self.n
    x.val = self.val
    return x

  def ones(self, n):
    """set n bits to 1"""
    self.n = n
    self.val = (1 << n) - 1

  def prepend(self, x):
    """pre-append bit buffer x"""
    self.val = (self.val << x.n) | x.val
    self.n += x.n

  def append(self, x):
    """append bit buffer x"""
    self.val |= (x.val << self.n)
    self.n += x.n

  def rm_head(self, n):
    """remove the first n bits"""
    if n < self.n:
      self.val >>= n
      self.n -= n
    else:
      self.n = 0
      self.val = 0

  def rm_tail(self, n):
    """remove the last n bits"""
    if n < self.n:
      self.n -= n
      self.val &= ((1 << self.n) - 1)
    else:
      self.n = 0
      self.val = 0

  def get_bytes(self):
    """return a byte array of the bits"""
    a = array.array('B')
    n = self.n
    val = self.val
    while n > 0:
      if n > 8:
        a.append(val & 255)
        val >>= 8
        n -= 8
      else:
        val &= (1 << n) - 1
        a.append(val)
        break
    return a

  def __str__(self):
    """return a tuple representation of the bit buffer"""
    s = []
    n = self.n
    val = self.val
    s.append('(%d,(' % self.n)
    s.extend(['0x%02x,' % x for x in self.get_bytes()])
    s.append('))')
    return ''.join(s)

  def __eq__(self, x):
    return (self.n == x.n) and (self.val == x.val)

  def __ne__(self, x):
    return not ((self.n == x.n) and (self.val == x.val))

#-----------------------------------------------------------------------------

class bits_old:

  def __init__(self, n = 0, val = 0):
    val &= ((1 << n) - 1)
    self.n = n
    self.val = val

  def clear(self):
    """remove any contents"""
    self.n = 0
    self.val = 0

  def ones(self, n):
    """set n bits to 1"""
    self.n = n
    self.val = (1 << n) - 1

  def zeroes(self, n):
    """set n bits to 0"""
    self.n = n
    self.val = 0

  def append_val(self, n, val):
    """append n bits from val to the bit buffer"""
    val &= ((1 << n) - 1)
    val <<= self.n
    self.val |= val
    self.n += n

  def append(self, bits):
    """append a bit buffer to the bit buffer"""
    self.append_val(bits.n, bits.val)

  def append_ones(self, n):
    """append n 1 bits to the bit buffer"""
    self.append_val(n, (1 << n) - 1)

  def append_zeroes(self, n):
    """append n 0 bits to the bit buffer"""
    self.append_val(n, 0)

  def append_str(self, s):
    """append bits from a 0/1 string"""
    self.append_val(len(s), int(s, 2))

  def append_tuple(self, t):
    """append bits from a 0/1 tuple"""
    x = 0
    for b in t:
      x = (x << 1) + b
    self.append_val(len(t), x)

  def append_tuple_reverse(self, t):
    """reverse a 0/1 tuple before appending"""
    l = list(t)
    l.reverse()
    self.append_tuple(l)

  def drop_lsb(self, n):
    """drop the least significant n bits"""
    if n < self.n:
      self.val >>= n
      self.n -= n
    else:
      self.n = 0
      self.val = 0

  def drop_msb(self, n):
    """drop the most significant n bits"""
    if n < self.n:
      self.n -= n
      self.val &= ((1 << self.n) - 1)
    else:
      self.n = 0
      self.val = 0

  def shr(self, bit_in = 0):
    """shift right"""
    bit_out = self.val & 1
    self.val >>= 1
    self.val |= (bit_in << (self.n - 1))
    return bit_out

  def reverse(self):
    """reverse the bits"""
    x = 0
    for i in xrange(self.n):
      if (self.val >> i) & 1:
        x |= 1 << (self.n - 1 - i)
    self.val = x

  def get(self):
    """return a byte array of the bits"""
    a = array.array('B')
    n = self.n
    val = self.val
    while n > 0:
      if n > 8:
        a.append(val & 255)
        val >>= 8
        n -= 8
      else:
        val &= (1 << n) - 1
        a.append(val)
        break
    return a

  def get_reverse(self):
    """reverse the bits before returning the byte array"""
    self.reverse()
    return self.get()

  def set(self, n, a):
    """set the bits from a byte array"""
    self.val = 0
    self.n = n
    for i in xrange(len(a) - 1, -1, -1):
      self.val <<= 8
      self.val |= a[i]

  def bit_str(self):
    """return a 0/1 string"""
    s = []
    for i in xrange(self.n - 1, -1, -1):
      s.append(('0', '1')[(self.val >> i) & 1])
    return ''.join(s)

  def scan(self, format):
    """using the format tuple, scan the buffer and return a tuple of values"""
    l = []
    val = self.val
    format_list = list(format)
    format_list.reverse()
    for n in format_list:
      mask = (1 << n) - 1
      l.append(val & mask)
      val >>= n
    l.reverse()
    return tuple(l)

  def __and__(self, x):
    return bits(min(self.n, x.n), self.val & x.val)

  def __eq__(self, x):
    return (self.n == x.n) and (self.val == x.val)

  def __ne__(self, x):
    return not ((self.n == x.n) and (self.val == x.val))

  def __str__(self):
    return '(%d) %x' % (self.n, self.val)

  def __len__(self):
    return self.n

#-----------------------------------------------------------------------------
