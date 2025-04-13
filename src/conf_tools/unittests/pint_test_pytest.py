import pytest
import logging
import pint
import sys
from io import StringIO

def test_pint_pixel_registration():
    """Test to check for the Pint pixel unit registration warning.
    
    This test checks if the warning from pint about redefining 'pixel' unit
    is expected behavior or a real issue. The warning occurs when mcdp imports
    conf_tools, which initializes its logger, and then later code creates a
    UnitRegistry that redefines the pixel unit.
    """
    # Set up logging capture
    log_capture = StringIO()
    handler = logging.StreamHandler(log_capture)
    log_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(log_format)
    
    # Get the pint logger and add our handler
    pint_logger = logging.getLogger('pint.util')
    pint_logger.addHandler(handler)
    pint_logger.setLevel(logging.WARNING)
    
    try:
        # Create UnitRegistry instances
        ureg1 = pint.UnitRegistry()
        
        # Define pixel unit
        ureg1.define('pixel = [pixel]')
        
        # Create a second registry which should trigger the warning
        ureg2 = pint.UnitRegistry()
        ureg2.define('pixel = [pixel]')
        
        # Check if warning was logged
        log_content = log_capture.getvalue()
        assert "Redefining 'pixel'" in log_content, "Expected warning about redefining pixel unit"
        
        # Verify we can use the unit despite the warning
        pixels = ureg2.Quantity(10, 'pixel')
        assert pixels.magnitude == 10
        assert str(pixels.units) == 'pixel'
        
        # Demonstrate that this is just a warning, not an error that affects functionality
        assert ureg2.Quantity(5, 'pixel') + ureg2.Quantity(5, 'pixel') == ureg2.Quantity(10, 'pixel')
    finally:
        # Clean up
        pint_logger.removeHandler(handler)

def test_pint_pixel_from_mcdp_posets():
    """Test that verifies the warning comes from mcdp_posets.rcomp_units module's
    MyUnitRegistry class, which defines pixels = [pixels] = pixel
    """
    # This test directly imports from mcdp to verify the source
    try:
        from mcdp_posets.rcomp_units import MyUnitRegistry
        
        # Set up logging capture
        log_capture = StringIO()
        handler = logging.StreamHandler(log_capture)
        log_format = logging.Formatter('%(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(log_format)
        
        # Get the pint logger and add our handler
        pint_logger = logging.getLogger('pint.util')
        pint_logger.addHandler(handler)
        pint_logger.setLevel(logging.WARNING)
        
        try:
            # Create an instance of MyUnitRegistry which should trigger the warning
            ureg = MyUnitRegistry()
            
            # Check if warning was logged
            log_content = log_capture.getvalue()
            assert "Redefining 'pixel'" in log_content, "Expected warning from MyUnitRegistry"
            
            # Verify pixel unit works correctly
            assert ureg.Quantity(10, 'pixel').magnitude == 10
        finally:
            # Clean up
            pint_logger.removeHandler(handler)
            
    except ImportError:
        pytest.skip("mcdp_posets not available in test environment")