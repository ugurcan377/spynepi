
from spyne.protocol.http import HttpRpc

class SpynepiHttpRpc(HttpRpc):
    def decompose_incoming_envelope(self, ctx, message):
        HttpRpc.decompose_incoming_envelope(self, ctx, message)

        ctx.method_request_string = '{http://usefulinc.com/ns/doap#}register'