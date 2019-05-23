# Copyright 2019 The Sonnet Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or  implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================

"""Tests for sonnet.v2.src.momentum."""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from absl.testing import parameterized
from sonnet.src import momentum as opt
from sonnet.src import test_utils
import tensorflow as tf


class MomentumTest(test_utils.TestCase, parameterized.TestCase):

  @parameterized.parameters(opt.Momentum, opt.ReferenceMomentum)
  def testDense(self, opt_class):
    parameters = [tf.Variable([1., 2.]), tf.Variable([3., 4.])]
    updates = [tf.constant([5., 5.]), tf.constant([3., 3.])]
    optimizer = opt_class(learning_rate=0.1, momentum=0.9)
    # Step 1 of Momentum
    optimizer.apply(updates, parameters)
    self.assertAllClose([[0.5, 1.5], [2.7, 3.7]],
                        [x.numpy() for x in parameters])
    # Step 2 of Momentum
    optimizer.apply(updates, parameters)
    self.assertAllClose([[-0.45, 0.55], [2.13, 3.13]],
                        [x.numpy() for x in parameters])
    # Step 3 of Momentum
    optimizer.apply(updates, parameters)
    self.assertAllClose([[-1.805, -0.805], [1.317, 2.317]],
                        [x.numpy() for x in parameters])

  @parameterized.parameters(opt.Momentum, opt.ReferenceMomentum)
  def testNoneUpdate(self, opt_class):
    parameters = [tf.Variable([1., 2.])]
    updates = [None]
    optimizer = opt_class(learning_rate=0.1, momentum=0.9)
    optimizer.apply(updates, parameters)
    self.assertAllClose([[1., 2.]], [x.numpy() for x in parameters])

  @parameterized.parameters(opt.Momentum, opt.ReferenceMomentum)
  def testVariableHyperParams(self, opt_class):
    parameters = [tf.Variable([1., 2.]), tf.Variable([3., 4.])]
    updates = [tf.constant([5., 5.]), tf.constant([3., 3.])]
    learning_rate = tf.Variable(0.1)
    momentum = tf.Variable(0.9)
    optimizer = opt_class(learning_rate=learning_rate, momentum=momentum)
    optimizer.apply(updates, parameters)
    self.assertAllClose([[0.5, 1.5], [2.7, 3.7]],
                        [x.numpy() for x in parameters])
    learning_rate.assign(0.01)
    momentum.assign(0.09)
    self.assertAlmostEqual(0.01, optimizer.learning_rate.numpy())
    self.assertAlmostEqual(0.09, optimizer.momentum.numpy())
    optimizer.apply(updates, parameters)
    self.assertAllClose([[0.4455, 1.4455], [2.6673, 3.6673]],
                        [x.numpy() for x in parameters])

  @parameterized.parameters(opt.Momentum, opt.ReferenceMomentum)
  def testHyperParamDTypeConversion(self, opt_class):
    parameters = [tf.Variable([1., 2.]), tf.Variable([3., 4.])]
    updates = [tf.constant([5., 5.]), tf.constant([3., 3.])]
    dtype = tf.float32 if self.primary_device == "TPU" else tf.float64
    learning_rate = tf.Variable(0.1, dtype=dtype)
    momentum = tf.Variable(0.9, dtype=dtype)
    optimizer = opt_class(learning_rate=learning_rate, momentum=momentum)
    optimizer.apply(updates, parameters)
    self.assertAllClose([[0.5, 1.5], [2.7, 3.7]],
                        [x.numpy() for x in parameters])

  @parameterized.parameters(opt.Momentum, opt.ReferenceMomentum)
  def testDifferentLengthUpdatesParams(self, opt_class):
    parameters = [tf.Variable([1., 2.]), tf.Variable([3., 4.])]
    updates = [tf.constant([5., 5.])]
    optimizer = opt_class(learning_rate=0.1, momentum=0.9)
    with self.assertRaisesRegexp(
        ValueError, "`updates` and `parameters` must be the same length."):
      optimizer.apply(updates, parameters)

  @parameterized.parameters(opt.Momentum, opt.ReferenceMomentum)
  def testEmptyParams(self, opt_class):
    optimizer = opt_class(learning_rate=0.1, momentum=0.9)
    with self.assertRaisesRegexp(ValueError, "`parameters` cannot be empty."):
      optimizer.apply([], [])

  @parameterized.parameters(opt.Momentum, opt.ReferenceMomentum)
  def testInconsistentDTypes(self, opt_class):
    parameters = [tf.Variable([1., 2.], name="param0")]
    updates = [tf.constant([5, 5])]
    optimizer = opt_class(learning_rate=0.1, momentum=0.9)
    with self.assertRaisesRegexp(
        ValueError, "DType of .* is not equal to that of parameter .*param0.*"):
      optimizer.apply(updates, parameters)

  @parameterized.parameters(opt.Momentum, opt.ReferenceMomentum)
  def testAccumulatorVariablesColocatedWithOriginal(self, opt_class):
    optimizer = opt_class(learning_rate=0.1, momentum=0.9)
    with tf.device("CPU:0"):
      var = tf.Variable(1.0)
    accum_var = optimizer._get_accumulated_momentum(var)
    self.assertEqual(accum_var.device, var.device)

if __name__ == "__main__":
  # tf.enable_v2_behavior()
  tf.test.main()