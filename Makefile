serve:
	flask run

protoc:
	./.venv/Scripts/python.exe -m grpc_tools.protoc -I=backend/proto --python_betterproto_out=backend/proto backend/proto/ei.proto