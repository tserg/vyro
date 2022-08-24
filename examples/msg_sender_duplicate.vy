# @version ^0.3.5

a: public(address)
b: public(address)

@external
def set_msg_sender():
    self.a = msg.sender
    self.b = msg.sender
