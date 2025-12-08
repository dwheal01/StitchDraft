"""Test to verify repeat syntax works after fix."""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from engine.domain.factories.chart_section_factory import ChartSectionFactory

factory = ChartSectionFactory()
raglan = factory.create_with_defaults(name='test_raglan', start_side='RS')
raglan.cast_on_start(122)
print('✓ Cast-on successful')

# Test the repeat syntax that was failing
raglan.repeat_rounds(['repeat(k1, p1)'], 1)
print('✓ Repeat syntax works!')
print(f'Current stitch count: {raglan.get_current_num_of_stitches()}')
print('✓ All tests passed')

