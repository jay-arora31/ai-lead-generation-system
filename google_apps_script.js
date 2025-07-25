/**
 * Google Apps Script for Lead Generation Data
 * Deploy this script to Google Apps Script and use the deployment URL as GOOGLE_SHEETS_ENDPOINT
 * 
 * Instructions:
 * 1. Create a new Google Sheets document
 * 2. Go to Extensions > Apps Script
 * 3. Replace the default code with this script
 * 4. Update the SHEET_ID variable below with your Google Sheets ID
 * 5. Deploy as a web app with execute permissions for "Anyone"
 * 6. Use the deployment URL as your GOOGLE_SHEETS_ENDPOINT
 */

// Configuration - UPDATE THESE VALUES
const SHEET_ID = 'sheet_id';
const SHEET_NAME = 'Leads'; // Name of the sheet tab

/**
 * Main function to handle HTTP POST requests
 */
function doPost(e) {
  try {
    // Parse the incoming JSON data
    const postData = JSON.parse(e.postData.contents);
    
    if (postData.action === 'addLeads' && postData.data) {
      const result = addLeadsToSheet(postData.data);
      return ContentService.createTextOutput(JSON.stringify(result)).setMimeType(ContentService.MimeType.JSON);
    }
    
    return ContentService.createTextOutput(JSON.stringify({
      success: false,
      message: 'Invalid action or missing data'
    })).setMimeType(ContentService.MimeType.JSON);
    
  } catch (error) {
    console.error('Error processing request:', error);
    return ContentService.createTextOutput(JSON.stringify({
      success: false,
      message: 'Error processing request: ' + error.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

/**
 * Add leads data to Google Sheets
 */
function addLeadsToSheet(leadsData) {
  try {
    // Validate input data
    if (!leadsData || !Array.isArray(leadsData) || leadsData.length === 0) {
      return {
        success: false,
        message: 'No leads data provided or data is empty'
      };
    }
    
    // Open the spreadsheet by ID (CRITICAL FIX)
    const spreadsheet = SpreadsheetApp.openById(SHEET_ID);
    let sheet = spreadsheet.getSheetByName(SHEET_NAME);
    
    // Define headers
    const headers = [
      'Timestamp',
      'Company Name',
      'Website',
      'Employee Count',
      'Industry',
      'Location',
      'Business Summary',
      'Hardware Opportunities',
      'Decision Maker Hint',
      'Contact Emails',
      'Decision Makers',
      'Personalized Message'
    ];
    
    // Create sheet if it doesn't exist
    if (!sheet) {
      sheet = spreadsheet.insertSheet(SHEET_NAME);
    }
    
    // Check if headers exist and add them if missing
    const shouldAddHeaders = checkAndAddHeaders(sheet, headers);
    
    if (shouldAddHeaders) {
      console.log('Headers were missing and have been added to the sheet');
    }
    
    // Get the last row to append data
    const lastRow = sheet.getLastRow();
    
    // Prepare data rows
    const rows = [];
    for (const lead of leadsData) {
      const row = [
        lead.generated_at || new Date().toISOString(),
        lead.company_name || '',
        lead.website || '',
        lead.employee_count || '',
        lead.industry || '',
        lead.location || '',
        lead.business_summary || '',
        lead.hardware_opportunities || '',
        lead.decision_maker_hint || '',
        lead.contact_emails || '',
        lead.decision_makers || '',
        lead.personalized_message || ''
      ];
      rows.push(row);
    }
    
    // Add data to sheet (with improved error handling)
    if (rows.length > 0) {
      const startRow = lastRow + 1;
      const numRows = rows.length;
      const numCols = rows[0].length;
      
      // Validate range before setting values
      if (numRows > 0 && numCols > 0) {
        const range = sheet.getRange(startRow, 1, numRows, numCols);
        range.setValues(rows);
        
        // Auto-resize columns
        sheet.autoResizeColumns(1, numCols);
        
        // Set text wrapping for message column (last column)
        if (sheet.getLastRow() > 1) {
          const messageColumnRange = sheet.getRange(2, numCols, sheet.getLastRow() - 1, 1);
          messageColumnRange.setWrap(true);
        }
      }
    }
    
    return {
      success: true,
      message: `Successfully added ${rows.length} leads to Google Sheets`,
      rowsAdded: rows.length,
      sheetId: SHEET_ID,
      sheetName: SHEET_NAME
    };
    
  } catch (error) {
    console.error('Error adding leads to sheet:', error);
    return {
      success: false,
      message: 'Error adding leads to sheet: ' + error.toString(),
      errorDetails: {
        name: error.name,
        message: error.message,
        stack: error.stack
      }
    };
  }
}

/**
 * Test function - you can run this manually to test the script
 */
function testAddLeads() {
  const testData = [
    {
      company_name: 'Test Company',
      website: 'https://test.com',
      employee_count: 100,
      industry: 'Technology',
      location: 'San Francisco, CA',
      business_summary: 'A test company for demo purposes',
      hardware_opportunities: 'Workstations, Servers',
      decision_maker_hint: 'CTO',
      contact_emails: 'cto@test.com',
      decision_makers: 'John Doe (CTO)',
      personalized_message: 'This is a test personalized message',
      generated_at: new Date().toISOString()
    }
  ];
  
  const result = addLeadsToSheet(testData);
  console.log('Test result:', result);
  return result;
}

/**
 * Check if headers exist in the sheet and add them if missing
 */
function checkAndAddHeaders(sheet, expectedHeaders) {
  try {
    const lastRow = sheet.getLastRow();
    const lastColumn = sheet.getLastColumn();
    
    // If sheet is completely empty, add headers
    if (lastRow === 0 || lastColumn === 0) {
      console.log('Sheet is empty, adding headers');
      addHeadersToSheet(sheet, expectedHeaders);
      return true;
    }
    
    // Check if first row contains our expected headers
    const firstRowRange = sheet.getRange(1, 1, 1, Math.max(lastColumn, expectedHeaders.length));
    const firstRowValues = firstRowRange.getValues()[0];
    
    // Check if first row matches our expected headers
    let hasCorrectHeaders = true;
    for (let i = 0; i < expectedHeaders.length; i++) {
      if (!firstRowValues[i] || firstRowValues[i].toString().trim() !== expectedHeaders[i]) {
        hasCorrectHeaders = false;
        break;
      }
    }
    
    // If headers don't match or are missing, add them
    if (!hasCorrectHeaders) {
      console.log('Headers are missing or incorrect, adding proper headers');
      
      // If there's existing data, insert a new row at the top
      if (lastRow > 0) {
        sheet.insertRowBefore(1);
      }
      
      addHeadersToSheet(sheet, expectedHeaders);
      return true;
    }
    
    console.log('Headers already exist and are correct');
    return false;
    
  } catch (error) {
    console.error('Error checking headers:', error);
    // If there's an error, try to add headers anyway
    addHeadersToSheet(sheet, expectedHeaders);
    return true;
  }
}

/**
 * Add formatted headers to the sheet
 */
function addHeadersToSheet(sheet, headers) {
  try {
    // Add headers to first row
    sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
    
    // Format headers
    const headerRange = sheet.getRange(1, 1, 1, headers.length);
    headerRange.setBackground('#4285f4');
    headerRange.setFontColor('white');
    headerRange.setFontWeight('bold');
    headerRange.setWrap(true);
    headerRange.setHorizontalAlignment('center');
    headerRange.setVerticalAlignment('middle');
    
    // Make header row a bit taller
    sheet.setRowHeight(1, 40);
    
    console.log(`Successfully added ${headers.length} headers to sheet`);
    
  } catch (error) {
    console.error('Error adding headers to sheet:', error);
    throw error;
  }
}

/**
 * Helper function to get sheet info (for debugging)
 */
function getSheetInfo() {
  try {
    const spreadsheet = SpreadsheetApp.openById(SHEET_ID);
    const sheet = spreadsheet.getSheetByName(SHEET_NAME);
    
    return {
      sheetExists: !!sheet,
      sheetName: SHEET_NAME,
      lastRow: sheet ? sheet.getLastRow() : 0,
      lastColumn: sheet ? sheet.getLastColumn() : 0,
      spreadsheetId: SHEET_ID,
      hasHeaders: sheet && sheet.getLastRow() > 0 ? sheet.getRange(1, 1).getValue() !== '' : false
    };
  } catch (error) {
    return {
      error: error.toString(),
      sheetId: SHEET_ID,
      sheetName: SHEET_NAME
    };
  }
} 