proto_library(index_dataset_proto SRCS index_dataset.proto)
cc_library(index_wrapper SRCS index_wrapper.cc DEPS index_dataset_proto fs)
cc_library(index_sampler SRCS index_sampler.cc DEPS index_wrapper)

if(WITH_PYTHON)
  py_proto_compile(index_dataset_py_proto SRCS index_dataset.proto)
endif()
