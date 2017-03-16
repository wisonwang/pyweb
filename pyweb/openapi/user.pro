/**

tourial: https://developers.google.com/protocol-buffers/docs/pythontutorial

compile: protoc -I=$SRC_DIR --python_out=$DST_DIR $SRC_DIR/simple.proto

compile grpc code: python -m grpc.tools.protoc -I. --python_out=. --grpc_python_out=. simple.proto

*/

syntax = "proto3";
option py_generic_services = true;

package spacelive.user;

message User{
  string name = 1;
  int32 id = 2;
  string request = 3;
}


message FooResponse{
  string name = 1;
  int32 id = 2;
  string response = 3;
}

service Foo {
  rpc request(FooRequest) returns(FooResponse);
}


