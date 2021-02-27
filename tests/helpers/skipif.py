# Copyright The PyTorch Lightning team.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from distutils.version import LooseVersion
from typing import Optional

import pytest
import torch
from pkg_resources import get_distribution

from pytorch_lightning.utilities import _TORCH_QUANTIZE_AVAILABLE

_MISS_QUANT_DEFAULT = 'fbgemm' not in torch.backends.quantized.supported_engines


def create_skipif(
    min_gpus: int = 0,
    min_torch: Optional[str] = None,
    pt_quant: bool = False,
) -> dict:
    """ Creating aggregated arguments for standatd pytest skipif, sot the usecase is::

        @pytest.mark.skipif(**create_skipif(min_torch="99"))
        def test_any_func(...):
            ...

    >>> from pprint import pprint
    >>> create_skipif(min_torch="99")
    {'condition': True, 'reason': 'test requires minimal version `torch>=99'}
    >>> create_skipif(min_torch="0.0")
    {'condition': False, 'reason': 'no reason, just go test it...'}
    """
    conditions = []
    reasons = []

    if min_gpus:
        conditions.append(torch.cuda.device_count() < 2)
        reasons.append(f"multi-GPU machine with at least {min_gpus}")

    if min_torch:
        torch_version = LooseVersion(get_distribution("torch").version)
        conditions.append(torch_version < LooseVersion(min_torch))
        reasons.append(f"minimal version `torch>={min_torch}")

    if pt_quant:
        conditions.append(not _TORCH_QUANTIZE_AVAILABLE or _MISS_QUANT_DEFAULT)
        reasons.append("PyTorch quantization")

    if not any(conditions):
        return dict(condition=False, reason="no reason, just go test it...")

    reasons = [rs for cond, rs in zip(conditions, reasons) if cond]
    reason = "test requires " + ' + '.join(reasons)
    return dict(condition=any(conditions), reason=reason)


@pytest.mark.skipif(**create_skipif(min_torch="99"))
def test_always_skip():
    exit(1)


@pytest.mark.skipif(**create_skipif(min_torch="0.0"))
def test_always_pass():
    assert True