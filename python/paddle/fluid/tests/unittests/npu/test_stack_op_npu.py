#  Copyright (c) 2021 PaddlePaddle Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import print_function

import numpy as np
import unittest
import sys
sys.path.append("..")
from op_test import OpTest
import paddle
import paddle.fluid as fluid
import paddle.fluid.core as core

paddle.enable_static()


@unittest.skipIf(not paddle.is_compiled_with_npu(),
                 "core is not compiled with NPU")
class TestStackOpBase(OpTest):
    def initDefaultParameters(self):
        self.num_inputs = 4
        self.input_dim = (5, 6, 7)
        self.axis = 0

    def initParameters(self):
        pass

    def get_x_names(self):
        x_names = []
        for i in range(self.num_inputs):
            x_names.append('x{}'.format(i))
        return x_names

    def setUp(self):
        self.initDefaultParameters()
        self.initParameters()
        self.op_type = 'stack'
        self.set_npu()
        self.init_dtype()
        self.x = []
        for i in range(self.num_inputs):
            self.x.append(
                np.random.random(size=self.input_dim).astype(self.dtype))

        tmp = []
        x_names = self.get_x_names()
        for i in range(self.num_inputs):
            tmp.append((x_names[i], self.x[i]))

        self.inputs = {'X': tmp}
        self.outputs = {'Y': np.stack(self.x, axis=self.axis)}
        self.attrs = {'axis': self.axis}

    def set_npu(self):
        self.__class__.use_npu = True
        self.place = paddle.NPUPlace(0)

    def init_dtype(self):
        self.dtype = np.float32

    def test_check_output(self):
        self.check_output_with_place(self.place)

    def test_check_grad(self):
        self.check_grad_with_place(self.place, self.get_x_names(), 'Y')


@unittest.skipIf(not paddle.is_compiled_with_npu(),
                 "core is not compiled with NPU")
class TestStackOp1(TestStackOpBase):
    def initParameters(self):
        self.num_inputs = 16


@unittest.skipIf(not paddle.is_compiled_with_npu(),
                 "core is not compiled with NPU")
class TestStackOp2(TestStackOpBase):
    def initParameters(self):
        self.num_inputs = 20


@unittest.skipIf(not paddle.is_compiled_with_npu(),
                 "core is not compiled with NPU")
class TestStackOp3(TestStackOpBase):
    def initParameters(self):
        self.axis = -1


@unittest.skipIf(not paddle.is_compiled_with_npu(),
                 "core is not compiled with NPU")
class TestStackOp4(TestStackOpBase):
    def initParameters(self):
        self.axis = -4


@unittest.skipIf(not paddle.is_compiled_with_npu(),
                 "core is not compiled with NPU")
class TestStackOp5(TestStackOpBase):
    def initParameters(self):
        self.axis = 1


@unittest.skipIf(not paddle.is_compiled_with_npu(),
                 "core is not compiled with NPU")
class TestStackOp6(TestStackOpBase):
    def initParameters(self):
        self.axis = 3


@unittest.skipIf(not paddle.is_compiled_with_npu(),
                 "core is not compiled with NPU")
class TestStackAPIWithLoDTensorArray(unittest.TestCase):
    """
    Test stack api when the input(x) is a LoDTensorArray.
    """

    def setUp(self):
        self.axis = 1
        self.iter_num = 3
        self.input_shape = [2, 3]
        self.x = np.random.random(self.input_shape).astype("float32")
        self.place = paddle.NPUPlace(0) \
            if paddle.is_compiled_with_npu() else paddle.CPUPlace()
        self.set_program()

    def set_program(self):
        self.program = fluid.Program()
        with fluid.program_guard(self.program):
            input = fluid.layers.assign(self.x)
            tensor_array = fluid.layers.create_array(dtype='float32')
            zero = fluid.layers.fill_constant(shape=[1], value=0, dtype="int64")

            for i in range(self.iter_num):
                fluid.layers.array_write(input, zero + i, tensor_array)

            self.out_var = fluid.layers.stack(tensor_array, axis=self.axis)

    def test_case(self):
        self.assertTrue(self.out_var.shape[self.axis] == -1)
        exe = fluid.Executor(self.place)
        res = exe.run(self.program, fetch_list=self.out_var)
        self.assertTrue(
            np.array_equal(
                res[0], np.stack(
                    [self.x] * self.iter_num, axis=self.axis)))


@unittest.skipIf(not paddle.is_compiled_with_npu(),
                 "core is not compiled with NPU")
class TestTensorStackAPIWithLoDTensorArray(unittest.TestCase):
    """
    Test stack api when the input(x) is a LoDTensorArray.
    """

    def setUp(self):
        self.axis = 1
        self.iter_num = 3
        self.input_shape = [2, 3]
        self.x = np.random.random(self.input_shape).astype("float32")
        self.place = paddle.NPUPlace(0) \
            if paddle.is_compiled_with_npu() else paddle.CPUPlace()
        self.set_program()

    def set_program(self):
        self.program = fluid.Program()
        with fluid.program_guard(self.program):
            input = fluid.layers.assign(self.x)
            tensor_array = fluid.layers.create_array(dtype='float32')
            zero = fluid.layers.fill_constant(shape=[1], value=0, dtype="int64")

            for i in range(self.iter_num):
                fluid.layers.array_write(input, zero + i, tensor_array)

            self.out_var = paddle.stack(tensor_array, axis=self.axis)

    def test_case(self):
        self.assertTrue(self.out_var.shape[self.axis] == -1)
        exe = fluid.Executor(self.place)
        res = exe.run(self.program, fetch_list=self.out_var)
        self.assertTrue(
            np.array_equal(
                res[0], np.stack(
                    [self.x] * self.iter_num, axis=self.axis)))


@unittest.skipIf(not paddle.is_compiled_with_npu(),
                 "core is not compiled with NPU")
class API_test(unittest.TestCase):
    def test_out(self):
        with fluid.program_guard(fluid.Program(), fluid.Program()):
            data1 = fluid.layers.data('data1', shape=[1, 2], dtype='float64')
            data2 = fluid.layers.data('data2', shape=[1, 2], dtype='float64')
            data3 = fluid.layers.data('data3', shape=[1, 2], dtype='float64')
            result_stack = paddle.stack([data1, data2, data3], axis=0)
            place = paddle.NPUPlace(0)
            exe = fluid.Executor(place)
            input1 = np.random.random([1, 2]).astype('float64')
            input2 = np.random.random([1, 2]).astype('float64')
            input3 = np.random.random([1, 2]).astype('float64')
            result, = exe.run(
                feed={"data1": input1,
                      "data2": input2,
                      "data3": input3},
                fetch_list=[result_stack])
            expected_result = np.stack([input1, input2, input3], axis=0)
            self.assertTrue(np.allclose(expected_result, result))

    def test_single_tensor_error(self):
        with fluid.program_guard(fluid.Program(), fluid.Program()):
            x = paddle.rand([2, 3])
            self.assertRaises(TypeError, paddle.stack, x)


@unittest.skipIf(not paddle.is_compiled_with_npu(),
                 "core is not compiled with NPU")
class API_DygraphTest(unittest.TestCase):
    def test_out(self):
        data1 = np.array([[1.0, 2.0]])
        data2 = np.array([[3.0, 4.0]])
        data3 = np.array([[5.0, 6.0]])
        with fluid.dygraph.guard(place=paddle.NPUPlace(0)):
            x1 = fluid.dygraph.to_variable(data1)
            x2 = fluid.dygraph.to_variable(data2)
            x3 = fluid.dygraph.to_variable(data3)
            result = paddle.stack([x1, x2, x3])
            result_np = result.numpy()
        expected_result = np.stack([data1, data2, data3])
        self.assertTrue(np.allclose(expected_result, result_np))

        with fluid.dygraph.guard(place=paddle.NPUPlace(0)):
            y1 = fluid.dygraph.to_variable(data1)
            result = paddle.stack([y1], axis=0)
            result_np_2 = result.numpy()
        expected_result_2 = np.stack([data1], axis=0)
        self.assertTrue(np.allclose(expected_result_2, result_np_2))

    def test_single_tensor_error(self):
        with fluid.dygraph.guard(place=paddle.NPUPlace(0)):
            x = paddle.to_tensor([1, 2, 3])
            self.assertRaises(Exception, paddle.stack, x)


if __name__ == '__main__':
    unittest.main()
