# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: lab6-grpc.proto
"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0flab6-grpc.proto\x12\x04lab6\"\x1e\n\x06\x61\x64\x64Msg\x12\t\n\x01\x61\x18\x01 \x01(\x05\x12\t\n\x01\x62\x18\x02 \x01(\x05\"\x1a\n\x0brawImageMsg\x12\x0b\n\x03img\x18\x01 \x01(\x0c\"%\n\rdotProductMsg\x12\t\n\x01\x61\x18\x01 \x03(\x02\x12\t\n\x01\x62\x18\x02 \x03(\x02\"\x1b\n\x0cjsonImageMsg\x12\x0b\n\x03img\x18\x01 \x01(\t\"\x17\n\x08\x61\x64\x64Reply\x12\x0b\n\x03sum\x18\x01 \x01(\x05\"%\n\x0f\x64otProductReply\x12\x12\n\ndotproduct\x18\x01 \x01(\x02\"+\n\nimageReply\x12\r\n\x05width\x18\x01 \x01(\x05\x12\x0e\n\x06height\x18\x02 \x01(\x05\x32\xf4\x01\n\x08Lab6Grpc\x12,\n\nPerformAdd\x12\x0c.lab6.addMsg\x1a\x0e.lab6.addReply\"\x00\x12\x38\n\x0fImageDimensions\x12\x11.lab6.rawImageMsg\x1a\x10.lab6.imageReply\"\x00\x12\x41\n\x11PerformDotProduct\x12\x13.lab6.dotProductMsg\x1a\x15.lab6.dotProductReply\"\x00\x12=\n\x13JsonImageDimensions\x12\x12.lab6.jsonImageMsg\x1a\x10.lab6.imageReply\"\x00\x62\x06proto3')

_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'lab6_grpc_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:

  DESCRIPTOR._options = None
  _ADDMSG._serialized_start=25
  _ADDMSG._serialized_end=55
  _RAWIMAGEMSG._serialized_start=57
  _RAWIMAGEMSG._serialized_end=83
  _DOTPRODUCTMSG._serialized_start=85
  _DOTPRODUCTMSG._serialized_end=122
  _JSONIMAGEMSG._serialized_start=124
  _JSONIMAGEMSG._serialized_end=151
  _ADDREPLY._serialized_start=153
  _ADDREPLY._serialized_end=176
  _DOTPRODUCTREPLY._serialized_start=178
  _DOTPRODUCTREPLY._serialized_end=215
  _IMAGEREPLY._serialized_start=217
  _IMAGEREPLY._serialized_end=260
  _LAB6GRPC._serialized_start=263
  _LAB6GRPC._serialized_end=507
# @@protoc_insertion_point(module_scope)
