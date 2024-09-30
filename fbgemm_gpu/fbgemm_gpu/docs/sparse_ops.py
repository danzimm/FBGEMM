# Copyright (c) Meta Platforms, Inc. and affiliates.
# All rights reserved.
#
# This source code is licensed under the BSD-style license found in the
# LICENSE file in the root directory of this source tree.

import torch

from .common import add_docs

add_docs(
    torch.ops.fbgemm.permute_2D_sparse_data,
    """
permute_2D_sparse_data(permute, lengths, values, weights=None, permuted_lengths_sum=None) -> Tuple[Tensor, Tensor, Optional[Tensor]]

Permute 2D sparse data along the first dimension (dim 0). Note that 2D
refers to the number of dense dimensions. The input data is actually 3D
where the first two dimensions are dense and the last dimension is
jagged (sparse). The data to permute over can be less or more and with or
without repetitions.

Args:
    permute (Tensor): A 1D-tensor that describes how data is permuted along dim
        0. `permute[i]` indicates that data at position `permute[i]` is moved
        to position `i`. The length of this tensor is the total amount of data
        in dim 0 to be permuted. The values in `permute` must be >= 0 and <
        `lengths.shape[0]`

    lengths (Tensor): A 2D-tensor that contains jagged shapes corresponding to
        the other two dense dimensions. For example, in the case of the
        embedding input, the 3D shape is (num features, batch size, bag size).
        `lengths[t][b]` represents the bag size of feature `t` and sample `b`.

    values (Tensor): A 1D-input-tensor to be permuted. The length of this
        tensor must be equal to `lengths.sum()`. This tensor can be of any data
        type.

    weights (Optional[Tensor] = None): An optional 1D-float-tensor. It must
        have the same length as `values`. It will be permuted the same way as
        values

    permuted_lengths_sum (Optional[int] = None): An optional value that
        represents the total number of elements in the permuted data (output
        shape). If not provided, the operator will compute this data which may
        cause a device-host synchronization (if using GPU). Thus, it is
        recommended to supply this value to avoid such the synchronization.

Returns:
    A tuple of permuted lengths, permuted indices and permuted weights

**Example:**

    >>> permute = torch.tensor([1, 0, 2], dtype=torch.int32, device="cuda")
    >>> lengths = torch.tensor([[2, 3, 4, 5], [1, 2, 4, 8], [0, 3, 2, 3]], dtype=torch.int64, device="cuda")
    >>> values = torch.randint(low=0, high=100, size=(lengths.sum().item(),), dtype=torch.int64, device="cuda")
    >>> print(values)
    tensor([29, 12, 61, 98, 56, 94,  5, 89, 65, 48, 71, 54, 40, 33, 78, 68, 42, 21,
            60, 51, 15, 47, 48, 68, 52, 19, 38, 30, 38, 97, 97, 98, 18, 40, 42, 89,
            66], device='cuda:0')
    >>> torch.ops.fbgemm.permute_2D_sparse_data(permute, lengths, values)
    (tensor([[1, 2, 4, 8],
             [2, 3, 4, 5],
             [0, 3, 2, 3]], device='cuda:0'),
     tensor([78, 68, 42, 21, 60, 51, 15, 47, 48, 68, 52, 19, 38, 30, 38, 29, 12, 61,
             98, 56, 94,  5, 89, 65, 48, 71, 54, 40, 33, 97, 97, 98, 18, 40, 42, 89,
             66], device='cuda:0'),
     None)
    """,
)

add_docs(
    torch.ops.fbgemm.permute_1D_sparse_data,
    """
permute_1D_sparse_data(permute, lengths, values, weights=None, permuted_lengths_sum=None) -> Tuple[Tensor, Tensor, Optional[Tensor]]

Permute 1D sparse data. Note that 1D referrs to the number of dense dimensions.
The input data is actually 2D where the first dimension is dense and the second
dimension is jagged (sparse).  The data to permute over can be less or more and
withh or without repetitions.

Args:
    permute (Tensor): A 1D-tensor that describes how data is permuted along dim
        0. `permute[i]` indicates that data at position `permute[i]` is moved
        to position `i`. The length of this tensor is the total amount of data
        in dim 0 to be permuted. The values in `permute` must be >= 0 and <
        `lengths.numel()`

    lengths (Tensor): A 1D-tensor that contains jagged shapes corresponding to
        the other dense dimension. `lengths[i]` represents the jagged shape of
        data at position `i` in dim 0

    values (Tensor): A 1D-input-tensor to be permuted. The length of this
        tensor must be equal to `lengths.sum()`. This tensor can be of any data
        type.

    weights (Optional[Tensor] = None): An optional 1D-float-tensor. It must
        have the same length as `values`. It will be permuted the same way as
        values

    permuted_lengths_sum (Optional[int] = None): An optional value that
        represents the total number of elements in the permuted data (output
        shape). If not provided, the operator will compute this data which may
        cause a device-host synchronization (if using GPU). Thus, it is
        recommended to supply this value to avoid such the synchronization.

Returns:
    A tuple of permuted lengths, permuted indices and permuted weights

**Example:**
    >>> permute = torch.tensor([1, 0, 3, 0], dtype=torch.int32, device="cuda")
    >>> lengths = torch.tensor([2, 3, 4, 5], dtype=torch.int64, device="cuda")
    >>> values = torch.randint(low=0, high=100, size=(lengths.sum().item(),), dtype=torch.int64, device="cuda")
    >>> print(values)
    tensor([ 1, 76, 24, 84, 94, 25, 15, 23, 31, 46,  9, 23, 34,  3],
           device='cuda:0')
    >>> torch.ops.fbgemm.permute_1D_sparse_data(permute, lengths, values)
    (tensor([3, 2, 5, 2], device='cuda:0'),
     tensor([24, 84, 94,  1, 76, 46,  9, 23, 34,  3,  1, 76], device='cuda:0'),
     None)
    """,
)

add_docs(
    torch.ops.fbgemm.expand_into_jagged_permute,
    """
expand_into_jagged_permute(permute, input_offset, output_offset, output_size) -> Tensor

Expand the sparse data permute index from feature dimension to batch dimension,
for cases where the sparse features has different batch sizes across ranks.

The op expands the permute from feature level to batch level by contiguously
mapping each bag of its corresponding features to the position the batch sits
on after feature permute. The op will automatically derive offset array of
feature and batch to compute the output permute.

Args:
    permute (Tensor): The feature level permute index.

    input_offset (Tensor): The exclusive offsets of feature-level length.

    output_offsets (Tensor): The exclusive offsets of feature-level permuted
        length.

    output_size (int): The number of elements in the output tensor

Returns:
    The output follows the following formula

    >>> output_permute[feature_offset[permute[feature]] + batch] <- bag_offset[batch]
    """,
)

add_docs(
    torch.ops.fbgemm.asynchronous_complete_cumsum,
    """
asynchronous_complete_cumsum(t_in) -> Tensor

Compute complete cumulative sum. For the GPU operator, the operator is
nonblocking asynchronous. For the CPU operator, it is a blocking operator.

Args:
    t_in (Tensor): An input tensor

Returns:
    The complete cumulative sum of `t_in`. Shape is `t_in.numel() + 1`

**Example:**

    >>> t_in = torch.tensor([7, 8, 2, 1, 0, 9, 4], dtype=torch.int64, device="cuda")
    >>> torch.ops.fbgemm.asynchronous_complete_cumsum(t_in)
    tensor([ 0,  7, 15, 17, 18, 18, 27, 31], device='cuda:0')
    """,
)

add_docs(
    torch.ops.fbgemm.offsets_range,
    """
offsets_range(offsets, range_size) -> Tensor

Generate an integer sequence from 0 to `(offsets[i+1] - offsets[i])` for every
`i`, where `0 <= i < offsets.numel()`

Args:
    offsets (Tensor): The offsets (complete cumulative sum values)

    range_size (int): The output size (the total sum)

Returns:
    A tensor that contains offsets range

**Example:**
    >>> # Generate example inputs
    >>> lengths = torch.tensor([3, 4, 1, 9, 3, 7], dtype=torch.int64, device="cuda")
    >>> offsets = torch.ops.fbgemm.asynchronous_complete_cumsum(lengths)
    >>> range_size = offsets[-1].item()
    >>> print(range_size)
    27
    >>> offsets = offsets[:-1]
    >>> print(offsets)
    tensor([ 0,  3,  7,  8, 17, 20], device='cuda:0')
    >>> # Invoke
    >>> torch.ops.fbgemm.offsets_range(offsets, range_size)
    tensor([0, 1, 2, 0, 1, 2, 3, 0, 0, 1, 2, 3, 4, 5, 6, 7, 8, 0, 1, 2, 0, 1, 2, 3,
            4, 5, 6], device='cuda:0')
    """,
)

add_docs(
    torch.ops.fbgemm.segment_sum_csr,
    """
segment_sum_csr(batch_size, csr_seg, values) -> Tensor

Sum values within each segment on the given CSR data where each row has the
same number of non-zero elements.

Args:
    batch_size (int): The row stride (number of non-zero elements in each row)

    csr_seg (Tensor): The complete cumulative sum of segment lengths. A segment
        length is the number of rows within each segment. The shape of the
        `csr_seg` tensor is `num_segments + 1` where `num_segments` is the
        number of segments.

    values (Tensor): The values tensor to be segment summed. The number of
        elements in the tensor must be multiple of `batch_size`

Returns:
    A tensor containing the segment sum results. Shape is the number of
    segments.

**Example:**

    >>> batch_size = 2
    >>> # Randomize inputs
    >>> lengths = torch.tensor([3, 4, 1], dtype=torch.int, device="cuda")
    >>> offsets = torch.ops.fbgemm.asynchronous_complete_cumsum(lengths)
    >>> print(offsets)
    tensor([0, 3, 7, 8], device='cuda:0', dtype=torch.int32)
    >>> values = torch.randn(lengths.sum().item() * batch_size, dtype=torch.float32, device="cuda")
    >>> print(values)
    tensor([-2.8642e-01,  1.6451e+00,  1.1322e-01,  1.7335e+00, -8.4700e-02,
            -1.2756e+00,  1.1206e+00,  9.6385e-01,  6.2122e-02,  1.3104e-03,
            2.2667e-01,  2.3113e+00, -1.1948e+00, -1.5463e-01, -1.0031e+00,
            -3.5531e-01], device='cuda:0')
    >>> # Invoke
    >>> torch.ops.fbgemm.segment_sum_csr(batch_size, offsets, values)
    tensor([ 1.8451,  3.3365, -1.3584], device='cuda:0')
    """,
)

add_docs(
    torch.ops.fbgemm.keyed_jagged_index_select_dim1,
    """
keyed_jagged_index_select_dim1(values, lengths, offsets, indices, batch_size, weights=None, selected_lengths_sum=None) -> List[Tensor]

Perform an index select operation on the batch dimension (dim 1) of the given
keyed jagged tensor (KJT) input. The same samples in the batch of every key
will be selected. Note that each KJT has 3 dimensions: (`num_keys`, `batch_size`,
jagged dim), where `num_keys` is the number of keys, and `batch_size` is the
batch size. This operator is similar to a permute operator.

Args:
    values (Tensor): The KJT values tensor which contains concatenated data of
        every key

    lengths (Tensor): The KJT lengths tensor which contains the jagged shapes
        of every key (dim 0) and sample (dim 1). Shape is `num_keys *
        batch_size`

    offsets (Tensor): The KJT offsets tensor which is the complete cumulative
        sum of `lengths`. Shape is `num_keys * batch_size + 1`

    indices (Tensor): The indices to select, i.e., samples in the batch to
        select. The values of `indices` must be >= 0 and < `batch_size`

    batch_size (int): The batch size (dim 1 of KJT)

    weights (Optional[Tensor] = None): An optional float tensor which will be
        selected the same way as `values`. Thus, it must have the same shape as
        `values`

    selected_lengths_sum (Optional[int] = None): An optional value that
        represents the total number of elements in the index select data
        (output shape). If not provided, the operator will compute this data
        which may cause a device-host synchronization (if using GPU). Thus, it
        is recommended to supply this value to avoid such the synchronization.

Returns:
    The index-select KJT tensor (as a list of values, lengths, and weights if
    `weights` is not None)

**Example:**

    >>> num_keys = 2
    >>> batch_size = 4
    >>> output_size = 3
    >>> # Randomize inputs
    >>> lengths = torch.randint(low=0, high=10, size=(batch_size * num_keys,), dtype=torch.int64, device="cuda")
    >>> print(lengths)
    tensor([8, 5, 1, 4, 2, 7, 5, 9], device='cuda:0')
    >>> offsets = torch.ops.fbgemm.asynchronous_complete_cumsum(lengths)
    >>> print(offsets)
    tensor([ 0,  8, 13, 14, 18, 20, 27, 32, 41], device='cuda:0')
    >>> indices = torch.randint(low=0, high=batch_size, size=(output_size,), dtype=torch.int64, device="cuda")
    >>> print(indices)
    tensor([3, 3, 1], device='cuda:0')
    >>> # Use torch.arange instead of torch.randn to simplify the example
    >>> values = torch.arange(lengths.sum().item(), dtype=torch.float32, device="cuda")
    >>> print(values)
    tensor([ 0.,  1.,  2.,  3.,  4.,  5.,  6.,  7.,  8.,  9., 10., 11., 12., 13.,
            14., 15., 16., 17., 18., 19., 20., 21., 22., 23., 24., 25., 26., 27.,
            28., 29., 30., 31., 32., 33., 34., 35., 36., 37., 38., 39., 40.],
           device='cuda:0')
    >>> # Invoke. Output = (output, lengths)
    >>> torch.ops.fbgemm.keyed_jagged_index_select_dim1(values, lengths, offsets, indices, batch_size)
    [tensor([14., 15., 16., 17., 14., 15., 16., 17.,  8.,  9., 10., 11., 12., 32.,
             33., 34., 35., 36., 37., 38., 39., 40., 32., 33., 34., 35., 36., 37.,
             38., 39., 40., 20., 21., 22., 23., 24., 25., 26.], device='cuda:0'),
     tensor([4, 4, 5, 9, 9, 7], device='cuda:0')]
    """,
)