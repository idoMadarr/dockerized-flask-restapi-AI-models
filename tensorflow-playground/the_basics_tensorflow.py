import tensorflow as tf

# print("TensorFlow version:", tf.__version__)

# RANK 0: Only just one value for the tensor
rank0_string_tensor = tf.Variable('just string!', tf.string)
rank0_number_tensor = tf.Variable(100, tf.int16)
rank0_floating_tensor = tf.Variable(3.564, tf.float64)

# RANK 1: One Array (not matter the length)
rank1_tensor = tf.Variable(['test', 'ok', 'tim'], tf.string)


# RANK 2: Multiply Arrays (not matter the length - but has to be equal)
rank2_tensor = tf.Variable([['test', 'ok', 'tim'], ['test', 'yes', 'hello']], tf.string)
# print(rank2_tensor)

example_tensor1 = tf.ones([1, 2, 3])                        # [ [1 1 1] [1 1 1] ]
# example_tensor1 = tf.ones([1, 2])                         # [ 1 1 ]
# example_tensor1 = tf.ones([2, 5])                         # [ [1 1 1 1 1] [1 1 1 1 1] ]
reshape_tensor1 = tf.reshape(example_tensor1, [2, 3, 1])    # [ [ 1 1 1 ] ] [ [ 1 1 1 ] ]

# print(example_tensor1)
# print(reshape_tensor1)

another_test_tensor = tf.zeros([3,3,3,3])
reshape_another_test_tensor = tf.reshape(another_test_tensor, [81])     # [ 0 0 0 0 0 ... ]  81 for 3 * 3 * 3 * 3
print(another_test_tensor)
print(reshape_another_test_tensor)
