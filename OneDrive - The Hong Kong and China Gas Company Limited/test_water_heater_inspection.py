import pytest
import os
import pandas as pd
import zipfile
from unittest.mock import MagicMock, patch, ANY
import tempfile
import shutil

# IMPORT YOUR false_ceiling_gas_water_heater_inspection MODULE HERE
# Assuming your script is named 'false_ceiling_gas_water_heater_inspection.py'. If it's different, rename the file or change this import.
import false_ceiling_gas_water_heater_inspection  
 

# --- Testing Pure Logic Functions ---

def test_parse_filename_standard():
    """Test a standard filename with all components present."""
    filename = "ProjectA-Tower1-1A-InspectorName-20-01-2025.jpg"
    result = false_ceiling_gas_water_heater_inspection.parse_filename_with_zeros(filename)
    
    assert result['Project'] == "ProjectA"
    assert result['Tower'] == "Tower1"
    assert result['Flat'] == "1A"
    assert result['Inspector'] == "InspectorName"
    assert result['Date'] == "20-01-2025"

def test_parse_filename_zeros_rule():
    """Test the '0' rule for Tower and Flat."""
    # Case: Tower is '0', Flat is '0'
    filename = "ProjectB-0-0-InspectorB-21-01-2025.jpg"
    result = false_ceiling_gas_water_heater_inspection.parse_filename_with_zeros(filename)
    assert result['Tower'] == ""
    assert result['Flat'] == ""

    # Case: Tower is NOT '0', Flat is '0'
    filename = "ProjectC-TowerX-0-InspectorC-22-01-2025.jpg"
    result = false_ceiling_gas_water_heater_inspection.parse_filename_with_zeros(filename)
    assert result['Tower'] == "TowerX"
    assert result['Flat'] == ""

def test_parse_filename_malformed_short():
    """Test filenames that don't match the standard format."""
    # Case: Less than 5 parts
    filename = "JustProjectName.jpg"
    result = false_ceiling_gas_water_heater_inspection.parse_filename_with_zeros(filename)
    assert result['Project'] == "JustProjectName"
    assert result['Tower'] == ""
    assert result['Flat'] == ""
    
    # Case: Empty string
    result = false_ceiling_gas_water_heater_inspection.parse_filename_with_zeros("")
    assert result['Project'] == ""

def test_parse_filename_complex_date():
    """Test if date parsing handles extra hyphens correctly."""
    filename = "Proj-T1-F1-Insp-2025-01-01.jpg"
    result = false_ceiling_gas_water_heater_inspection.parse_filename_with_zeros(filename)
    assert result['Date'] == "2025-01-01"

def test_create_embedded_template():
    """Test if the DOCX template is created correctly."""
    with tempfile.TemporaryDirectory() as tmpdir:
        save_path = os.path.join(tmpdir, "template.docx")
        
        # execution of the function
        false_ceiling_gas_water_heater_inspection.create_embedded_template(save_path)
        
        # Verify file exists
        assert os.path.exists(save_path)