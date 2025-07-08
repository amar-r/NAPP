"""
Frontend pages for NAPP using FastHTML

Provides a modern, responsive interface for:
- Submitting new payroll entries
- Viewing payroll history in a table
- Exporting data with filters
- Auto-updating functionality
"""

from fasthtml.common import *
from typing import List
from app.models import PayrollEntry

def get_home_page_html(entries: List[PayrollEntry]) -> str:
    """Main home page with payroll management interface - returns raw HTML string."""
    
    # Generate table rows
    table_rows = ""
    for entry in entries:
        # Calculate total federal tax
        total_federal_tax = entry.federal_income_tax + entry.federal_social_security_tax + entry.federal_medicare_tax
        # Calculate total state tax
        total_state_tax = entry.virginia_income_tax + entry.virginia_unemployment_tax
        
        table_rows += f"""
        <tr>
            <td class="checkbox-cell">
                <input type="checkbox" name="entry_ids" value="{entry.id}" onchange="updateDeleteButton()">
            </td>
            <td>{entry.week_start_date}</td>
            <td>{entry.week_end_date}</td>
            <td style="text-align: right;">${entry.gross_pay:,.2f}</td>
            <td style="text-align: right;">${total_federal_tax:,.2f}</td>
            <td style="text-align: right;">${total_state_tax:,.2f}</td>
            <td style="text-align: right;">${entry.net_pay:,.2f}</td>
            <td>{entry.notes or ''}</td>
        </tr>
        """
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>NAPP - Nanny Automated Payroll Profiler</title>
        <style>
            body {{ 
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f0f0f0;
            }}
            
            h1 {{ 
                color: #333; 
                text-align: center; 
                margin-bottom: 30px;
            }}
            
            h2 {{ 
                color: #666; 
                margin-bottom: 10px;
            }}
            
            p {{
                margin: 5px 0;
            }}
            
            .summary-box {{
                background: lightblue; 
                padding: 20px; 
                margin: 20px 0; 
                border-radius: 8px;
            }}
            
            .form-box {{
                background: lightgreen; 
                padding: 20px; 
                margin: 20px 0; 
                border-radius: 8px;
            }}
            
            .table-box {{
                background: lightyellow; 
                padding: 20px; 
                margin: 20px 0; 
                border-radius: 8px;
            }}
            
            .table-actions {{
                margin-bottom: 15px;
                display: flex;
                gap: 10px;
                align-items: center;
            }}
            
            .export-btn {{
                background: #28a745;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
            }}
            
            .export-btn:hover {{
                background: #218838;
            }}
            
            .export-btn.secondary {{
                background: #17a2b8;
            }}
            
            .export-btn.secondary:hover {{
                background: #138496;
            }}
            
            .delete-btn {{
                background: #dc3545;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 14px;
            }}
            
            .delete-btn:hover {{
                background: #c82333;
            }}
            
            .delete-btn:disabled {{
                background: #6c757d;
                cursor: not-allowed;
            }}
            
            label {{
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
            }}
            
            input, textarea {{
                width: 100%;
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                box-sizing: border-box;
                margin-bottom: 15px;
            }}
            
            input[type="checkbox"] {{
                width: auto;
                margin: 0;
            }}
            
            button {{
                background: #007bff;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 16px;
            }}
            
            button:hover {{
                background: #0056b3;
            }}
            
            table {{
                border-collapse: collapse;
                width: 100%;
                margin: 20px 0;
                background: white;
                border: 1px solid #ddd;
            }}
            
            th, td {{
                border: 1px solid #ddd;
                padding: 8px;
            }}
            
            th {{
                background-color: #f8f9fa;
                font-weight: bold;
            }}
            
            .checkbox-cell {{
                width: 30px;
                text-align: center;
            }}
        </style>
        <script>
            function updateDeleteButton() {{
                const checkboxes = document.querySelectorAll('input[name="entry_ids"]:checked');
                const deleteBtn = document.getElementById('deleteSelectedBtn');
                deleteBtn.disabled = checkboxes.length === 0;
            }}
            
            function deleteSelectedEntries() {{
                const checkboxes = document.querySelectorAll('input[name="entry_ids"]:checked');
                if (checkboxes.length === 0) {{
                    alert('Please select entries to delete.');
                    return;
                }}
                
                if (!confirm(`Are you sure you want to delete ${{checkboxes.length}} selected entries?`)) {{
                    return;
                }}
                
                const entryIds = Array.from(checkboxes).map(cb => cb.value);
                
                fetch('/payroll/delete', {{
                    method: 'POST',
                    headers: {{
                        'Content-Type': 'application/json',
                    }},
                    body: JSON.stringify({{entry_ids: entryIds}})
                }})
                .then(response => response.json())
                .then(data => {{
                    if (data.success) {{
                        alert(`Successfully deleted ${{data.deleted_count}} entries.`);
                        location.reload();
                    }} else {{
                        alert('Error deleting entries: ' + data.message);
                    }}
                }})
                .catch(error => {{
                    console.error('Error:', error);
                    alert('Error deleting entries. Please try again.');
                }});
            }}
            
            function exportToCSV() {{
                const checkboxes = document.querySelectorAll('input[name="entry_ids"]:checked');
                const entryIds = Array.from(checkboxes).map(cb => cb.value);
                
                // If no entries selected, export all
                const url = entryIds.length > 0 
                    ? `/payroll/export-csv?entry_ids=${{entryIds.join(',')}}`
                    : '/payroll/export-csv';
                
                window.location.href = url;
            }}
            
            function exportToJSON() {{
                const checkboxes = document.querySelectorAll('input[name="entry_ids"]:checked');
                const entryIds = Array.from(checkboxes).map(cb => cb.value);
                
                // If no entries selected, export all
                const url = entryIds.length > 0 
                    ? `/payroll/export-json?entry_ids=${{entryIds.join(',')}}`
                    : '/payroll/export-json';
                
                window.location.href = url;
            }}
            
            function addAnotherEntry() {{
                const form = document.querySelector('form[action="/payroll/new"]');
                const submitBtn = form.querySelector('button[type="submit"]');
                const addAnotherBtn = document.getElementById('addAnotherBtn');
                const resetBtn = document.getElementById('resetBtn');
                const additionalForms = document.getElementById('additionalEntryForms');
                
                // Change form action to add another
                form.dataset.addAnother = 'true';
                
                // Update button text
                submitBtn.textContent = 'Create All Entries';
                addAnotherBtn.style.display = 'none';
                resetBtn.style.display = 'inline-block';
                
                // Show additional forms container
                additionalForms.style.display = 'block';
                
                // Show first additional form
                showAdditionalForm(2);
                
                // Show instruction
                showMessage('Form is now in "Add Multiple Entries" mode. Use the buttons below to add more forms (up to 5 total).', 'success');
            }}
            
            function showAdditionalForm(formNumber) {{
                const formDiv = document.getElementById(`entryForm${{formNumber}}`);
                if (formDiv) {{
                    formDiv.style.display = 'block';
                    updateSubmitButtonText();
                }}
            }}
            
            function hideAdditionalForm(formNumber) {{
                const formDiv = document.getElementById(`entryForm${{formNumber}}`);
                if (formDiv) {{
                    formDiv.style.display = 'none';
                    formDiv.querySelector('form').reset();
                    updateSubmitButtonText();
                }}
            }}
            
            function updateSubmitButtonText() {{
                const visibleForms = document.querySelectorAll('.additional-form[style*="display: block"]');
                const totalEntries = 1 + visibleForms.length;
                const submitBtn = document.querySelector('form[action="/payroll/new"] button[type="submit"]');
                if (submitBtn && submitBtn.textContent.includes('Create')) {{
                    submitBtn.textContent = 'Create ' + totalEntries + ' Entries';
                }}
            }}
            
            function resetFormMode() {{
                const form = document.querySelector('form[action="/payroll/new"]');
                const submitBtn = form.querySelector('button[type="submit"]');
                const addAnotherBtn = document.getElementById('addAnotherBtn');
                const resetBtn = document.getElementById('resetBtn');
                const additionalForms = document.getElementById('additionalEntryForms');
                
                // Reset form action
                delete form.dataset.addAnother;
                
                // Update button text
                submitBtn.textContent = 'Create Entry';
                addAnotherBtn.style.display = 'inline-block';
                resetBtn.style.display = 'none';
                
                // Hide all additional forms
                additionalForms.style.display = 'none';
                document.querySelectorAll('.additional-form').forEach(formDiv => {{
                    formDiv.style.display = 'none';
                    formDiv.querySelector('form').reset();
                }});
            }}
            
            function submitPayrollForm(event) {{
                event.preventDefault();
                
                const form = event.target;
                const isAddAnotherMode = form.dataset.addAnother === 'true';
                
                if (isAddAnotherMode) {{
                    // Submit all forms simultaneously
                    submitAllEntries();
                }} else {{
                    // Submit single form
                    submitSingleEntry(form);
                }}
            }}
            
            function submitSingleEntry(form) {{
                const formData = new FormData(form);
                
                // Show loading state
                const submitBtn = form.querySelector('button[type="submit"]');
                const originalText = submitBtn.textContent;
                submitBtn.textContent = 'Creating...';
                submitBtn.disabled = true;
                
                fetch('/payroll/new', {{
                    method: 'POST',
                    body: formData
                }})
                .then(response => response.text())
                .then(html => {{
                    // Update the table section with new content
                    const tableBox = document.querySelector('.table-box');
                    const newTableBox = document.createElement('div');
                    newTableBox.innerHTML = html;
                    
                    // Extract the table content from the response
                    const newTable = newTableBox.querySelector('.table-box');
                    if (newTable) {{
                        tableBox.innerHTML = newTable.innerHTML;
                    }}
                    
                    // Reset form
                    form.reset();
                    
                    // Show success message
                    showMessage('Payroll entry created successfully!', 'success');
                    
                    // Update delete button count
                    updateDeleteButton();
                }})
                .catch(error => {{
                    console.error('Error:', error);
                    showMessage('Error creating payroll entry. Please try again.', 'error');
                }})
                .finally(() => {{
                    // Restore button state
                    submitBtn.textContent = originalText;
                    submitBtn.disabled = false;
                }});
            }}
            
            function hideAllAdditionalForms() {{
                for (let i = 2; i <= 5; i++) {{
                    hideAdditionalForm(i);
                }}
            }}
            
            function submitAllEntries() {{
                const mainForm = document.querySelector('form[action="/payroll/new"]');
                const additionalForms = document.querySelectorAll('.additional-form form');
                
                // Validate all forms
                if (!mainForm.checkValidity()) {{
                    showMessage('Please fill out the main form completely.', 'error');
                    return;
                }}
                
                // Count how many additional forms are visible and have data
                let visibleForms = [];
                for (let i = 0; i < additionalForms.length; i++) {{
                    const form = additionalForms[i];
                    const parentDiv = form.closest('.additional-form');
                    if (parentDiv.style.display !== 'none') {{
                        if (!form.checkValidity()) {{
                            showMessage('Please fill out Entry ' + (i + 2) + ' completely.', 'error');
                            return;
                        }}
                        visibleForms.push(form);
                    }}
                }}
                
                // Show loading state
                const submitBtn = mainForm.querySelector('button[type="submit"]');
                const originalText = submitBtn.textContent;
                const totalEntries = 1 + visibleForms.length;
                submitBtn.textContent = 'Creating ' + totalEntries + ' Entries...';
                submitBtn.disabled = true;
                
                // Submit main entry first
                const mainFormData = new FormData(mainForm);
                
                fetch('/payroll/new', {{
                    method: 'POST',
                    body: mainFormData
                }})
                .then(response => response.text())
                .then(html => {{
                    // Submit additional entries sequentially
                    let currentPromise = Promise.resolve();
                    
                    for (let i = 0; i < visibleForms.length; i++) {{
                        const form = visibleForms[i];
                        const formData = new FormData(form);
                        
                        currentPromise = currentPromise.then(() => {{
                            return fetch('/payroll/new', {{
                                method: 'POST',
                                body: formData
                            }});
                        }}).then(response => response.text());
                    }}
                    
                    return currentPromise;
                }})
                .then(finalHtml => {{
                    // Update the table section with new content
                    const tableBox = document.querySelector('.table-box');
                    const newTableBox = document.createElement('div');
                    newTableBox.innerHTML = finalHtml;
                    
                    // Extract the table content from the response
                    const newTable = newTableBox.querySelector('.table-box');
                    if (newTable) {{
                        tableBox.innerHTML = newTable.innerHTML;
                    }}
                    
                    // Reset all forms
                    mainForm.reset();
                    visibleForms.forEach(form => form.reset());
                    
                    // Show success message
                    showMessage('Successfully created ' + totalEntries + ' payroll entries!', 'success');
                    
                    // Update delete button count
                    updateDeleteButton();
                }})
                .catch(error => {{
                    console.error('Error:', error);
                    showMessage('Error creating payroll entries. Please try again.', 'error');
                }})
                .finally(() => {{
                    // Restore button state
                    submitBtn.textContent = originalText;
                    submitBtn.disabled = false;
                }});
            }}
            
            function showMessage(message, type) {{
                // Remove existing messages
                const existingMessages = document.querySelectorAll('.message');
                existingMessages.forEach(msg => msg.remove());
                
                // Create new message
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${{type}}`;
                messageDiv.textContent = message;
                messageDiv.style.cssText = `
                    padding: 10px 15px;
                    margin: 10px 0;
                    border-radius: 4px;
                    font-weight: bold;
                    ${{type === 'success' ? 'background: #d4edda; color: #155724; border: 1px solid #c3e6cb;' : 'background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb;'}}
                `;
                
                // Insert message after the form
                const formBox = document.querySelector('.form-box');
                formBox.appendChild(messageDiv);
                
                // Auto-remove after 5 seconds
                setTimeout(() => {{
                    messageDiv.remove();
                }}, 5000);
            }}
        </script>
    </head>
    <body>
        <h1>NAPP - Nanny Automated Payroll Profiler</h1>
        
        <div class="summary-box">
            <h2>Payroll Summary</h2>
            <p>Total Entries: {len(entries)}</p>
            <p>Total Gross Pay: ${sum(e.gross_pay for e in entries):,.2f}</p>
        </div>
        
        <div class="form-box">
            <h2>Create New Payroll Entry</h2>
            <form action="/payroll/new" method="post" onsubmit="submitPayrollForm(event)">
                <label for="week_start_date">Week Start Date:</label>
                <input type="date" id="week_start_date" name="week_start_date" required>
                
                <label for="week_end_date">Week End Date:</label>
                <input type="date" id="week_end_date" name="week_end_date" required>
                
                <label for="gross_pay">Gross Pay ($):</label>
                <input type="number" id="gross_pay" name="gross_pay" step="0.01" min="0" required>
                
                <label for="notes">Notes:</label>
                <textarea id="notes" name="notes" rows="3"></textarea>
                
                <div style="display: flex; gap: 10px; margin-top: 15px;">
                    <button type="submit">Create Entry</button>
                    <button type="button" id="addAnotherBtn" onclick="addAnotherEntry()" style="background: #6c757d;">
                        Add Multiple Entries
                    </button>
                    <button type="button" onclick="resetFormMode()" style="background: #ffc107; color: #212529; display: none;" id="resetBtn">
                        Reset Mode
                    </button>
                </div>
            </form>
            
            <!-- Additional entry forms (hidden by default) -->
            <div id="additionalEntryForms" style="display: none;">
                <div style="margin: 20px 0; padding: 10px; background: #f8f9fa; border-radius: 4px;">
                    <strong>Form Controls:</strong>
                    <button type="button" onclick="showAdditionalForm(2)" style="margin: 0 5px; padding: 5px 10px; background: #28a745; color: white; border: none; border-radius: 3px; cursor: pointer;">Add Entry 2</button>
                    <button type="button" onclick="showAdditionalForm(3)" style="margin: 0 5px; padding: 5px 10px; background: #28a745; color: white; border: none; border-radius: 3px; cursor: pointer;">Add Entry 3</button>
                    <button type="button" onclick="showAdditionalForm(4)" style="margin: 0 5px; padding: 5px 10px; background: #28a745; color: white; border: none; border-radius: 3px; cursor: pointer;">Add Entry 4</button>
                    <button type="button" onclick="showAdditionalForm(5)" style="margin: 0 5px; padding: 5px 10px; background: #28a745; color: white; border: none; border-radius: 3px; cursor: pointer;">Add Entry 5</button>
                    <button type="button" onclick="hideAllAdditionalForms()" style="margin: 0 5px; padding: 5px 10px; background: #dc3545; color: white; border: none; border-radius: 3px; cursor: pointer;">Hide All</button>
                </div>
                
                <div id="entryForm2" class="additional-form" style="display: none; margin-top: 30px; padding-top: 20px; border-top: 2px solid #ddd;">
                    <h3>Entry 2</h3>
                    <form action="/payroll/new" method="post">
                        <label for="week_start_date2">Week Start Date:</label>
                        <input type="date" id="week_start_date2" name="week_start_date" required>
                        
                        <label for="week_end_date2">Week End Date:</label>
                        <input type="date" id="week_end_date2" name="week_end_date" required>
                        
                        <label for="gross_pay2">Gross Pay ($):</label>
                        <input type="number" id="gross_pay2" name="gross_pay" step="0.01" min="0" required>
                        
                        <label for="notes2">Notes:</label>
                        <textarea id="notes2" name="notes" rows="3"></textarea>
                    </form>
                </div>
                
                <div id="entryForm3" class="additional-form" style="display: none; margin-top: 30px; padding-top: 20px; border-top: 2px solid #ddd;">
                    <h3>Entry 3</h3>
                    <form action="/payroll/new" method="post">
                        <label for="week_start_date3">Week Start Date:</label>
                        <input type="date" id="week_start_date3" name="week_start_date" required>
                        
                        <label for="week_end_date3">Week End Date:</label>
                        <input type="date" id="week_end_date3" name="week_end_date" required>
                        
                        <label for="gross_pay3">Gross Pay ($):</label>
                        <input type="number" id="gross_pay3" name="gross_pay" step="0.01" min="0" required>
                        
                        <label for="notes3">Notes:</label>
                        <textarea id="notes3" name="notes" rows="3"></textarea>
                    </form>
                </div>
                
                <div id="entryForm4" class="additional-form" style="display: none; margin-top: 30px; padding-top: 20px; border-top: 2px solid #ddd;">
                    <h3>Entry 4</h3>
                    <form action="/payroll/new" method="post">
                        <label for="week_start_date4">Week Start Date:</label>
                        <input type="date" id="week_start_date4" name="week_start_date" required>
                        
                        <label for="week_end_date4">Week End Date:</label>
                        <input type="date" id="week_end_date4" name="week_end_date" required>
                        
                        <label for="gross_pay4">Gross Pay ($):</label>
                        <input type="number" id="gross_pay4" name="gross_pay" step="0.01" min="0" required>
                        
                        <label for="notes4">Notes:</label>
                        <textarea id="notes4" name="notes" rows="3"></textarea>
                    </form>
                </div>
                
                <div id="entryForm5" class="additional-form" style="display: none; margin-top: 30px; padding-top: 20px; border-top: 2px solid #ddd;">
                    <h3>Entry 5</h3>
                    <form action="/payroll/new" method="post">
                        <label for="week_start_date5">Week Start Date:</label>
                        <input type="date" id="week_start_date5" name="week_start_date" required>
                        
                        <label for="week_end_date5">Week End Date:</label>
                        <input type="date" id="week_end_date5" name="week_end_date" required>
                        
                        <label for="gross_pay5">Gross Pay ($):</label>
                        <input type="number" id="gross_pay5" name="gross_pay" step="0.01" min="0" required>
                        
                        <label for="notes5">Notes:</label>
                        <textarea id="notes5" name="notes" rows="3"></textarea>
                    </form>
                </div>
            </div>
        </div>
        
        <div class="table-box">
            <h2>Payroll History</h2>
            <div class="table-actions">
                <button class="export-btn" onclick="exportToCSV()">
                    Export to CSV
                </button>
                <button class="export-btn secondary" onclick="exportToJSON()">
                    Export to JSON
                </button>
                <button id="deleteSelectedBtn" class="delete-btn" onclick="deleteSelectedEntries()" disabled>
                    Delete Selected ({len(entries)} entries)
                </button>
            </div>
            <table>
                <thead>
                    <tr>
                        <th class="checkbox-cell">
                            <input type="checkbox" onclick="toggleAllEntries(this)">
                        </th>
                        <th>Week Start</th>
                        <th>Week End</th>
                        <th style="text-align: right;">Gross Pay</th>
                        <th style="text-align: right;">Federal Tax</th>
                        <th style="text-align: right;">State Tax</th>
                        <th style="text-align: right;">Net Pay</th>
                        <th>Notes</th>
                    </tr>
                </thead>
                <tbody>
                    {table_rows}
                </tbody>
            </table>
        </div>
        
        <script>
            function toggleAllEntries(checkbox) {{
                const entryCheckboxes = document.querySelectorAll('input[name="entry_ids"]');
                entryCheckboxes.forEach(cb => {{
                    cb.checked = checkbox.checked;
                }});
                updateDeleteButton();
            }}
        </script>
    </body>
    </html>
    """
    
    return html

def get_home_page(entries: List[PayrollEntry]):
    """Main home page with payroll management interface."""
    return Div(
        H1('NAPP - Nanny Automated Payroll Profiler'),
        
        # Payroll Summary
        Div(
            H2('Payroll Summary'),
            P(f'Total Entries: {len(entries)}'),
            P(f'Total Gross Pay: ${sum(e.gross_pay for e in entries):,.2f}'),
            style='background: lightblue; padding: 20px; margin: 20px 0; border-radius: 8px;'
        ),
        
        # Payroll Entry Form
        Div(
            H2('Create New Payroll Entry'),
            Form(
                i=[
                    Div(
                        Label('Week Start Date:'),
                        Input(name='week_start_date', type='date', required=True),
                        style='margin-bottom: 15px;'
                    ),
                    Div(
                        Label('Week End Date:'),
                        Input(name='week_end_date', type='date', required=True),
                        style='margin-bottom: 15px;'
                    ),
                    Div(
                        Label('Gross Pay ($):'),
                        Input(name='gross_pay', type='number', step='0.01', min='0', required=True),
                        style='margin-bottom: 15px;'
                    ),
                    Div(
                        Label('Notes:'),
                        Textarea(name='notes', rows='3'),
                        style='margin-bottom: 15px;'
                    ),
                    Button('Create Entry', type='submit', style='background: #007bff; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer;')
                ],
                action='/payroll/new',
                method='post'
            ),
            style='background: lightgreen; padding: 20px; margin: 20px 0; border-radius: 8px;'
        ),
        
        # Payroll History Table
        Div(
            H2('Payroll History'),
            Table(
                thead=Thead(
                    Tr(
                        Th('Week Start'),
                        Th('Week End'),
                        Th('Gross Pay', style='text-align: right;'),
                        Th('Federal Tax', style='text-align: right;'),
                        Th('State Tax', style='text-align: right;'),
                        Th('Net Pay', style='text-align: right;'),
                        Th('Notes')
                    )
                ),
                tbody=Tbody(
                    *[Tr(
                        Td(entry.week_start_date),
                        Td(entry.week_end_date),
                        Td(f'${entry.gross_pay:,.2f}', style='text-align: right;'),
                        Td(f'${entry.federal_tax:,.2f}', style='text-align: right;'),
                        Td(f'${entry.state_tax:,.2f}', style='text-align: right;'),
                        Td(f'${entry.net_pay:,.2f}', style='text-align: right;'),
                        Td(entry.notes or '')
                    ) for entry in entries]
                ),
                style='width: 100%; border-collapse: collapse; margin-top: 15px;'
            ),
            style='background: lightyellow; padding: 20px; margin: 20px 0; border-radius: 8px;'
        ),
        
        Style('''
            body { 
                font-family: Arial, sans-serif;
                margin: 20px;
                background-color: #f0f0f0;
            }
            
            h1 { 
                color: #333; 
                text-align: center; 
                margin-bottom: 30px;
            }
            
            h2 { 
                color: #666; 
                margin-bottom: 10px;
            }
            
            p {
                margin: 5px 0;
            }
            
            label {
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
            }
            
            input, textarea {
                width: 100%;
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                box-sizing: border-box;
            }
            
            table {
                border-collapse: collapse;
                width: 100%;
                margin: 20px 0;
                background: white;
                border: 1px solid #ddd;
            }
            
            th, td {
                border: 1px solid #ddd;
                padding: 8px;
            }
            
            th {
                background-color: #f8f9fa;
                font-weight: bold;
            }
            
            button {
                background: #007bff;
                color: white;
                padding: 8px 16px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
            }
            
            button:hover {
                background: #0056b3;
            }
        ''')
    )
