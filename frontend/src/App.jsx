import React, { useState, useEffect } from 'react';
import { AlertTriangle, CheckCircle, Lock, ShieldAlert, FileSpreadsheet, Activity } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

function App() {
  const [records, setRecords] = useState([]);
  const [filterStatus, setFilterStatus] = useState('');
  const [loading, setLoading] = useState(true);

  // 1. Fetch live normalized data ledger from Django API REST Layer
  const fetchLedgerData = async (statusFilter = '') => {
    setLoading(true);
    try {
      // Aligned with the direct /ledger/ root routing prefix
      const url = statusFilter
        ? `http://127.0.0.1:8000/ledger/?status=${statusFilter}`
        : 'http://127.0.0.1:8000/ledger/';
      const response = await fetch(url);
      const data = await response.json();
      setRecords(data);
    } catch (error) {
      console.error("API Fetch Error:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLedgerData(filterStatus);
  }, [filterStatus]);

  // 2. Handle compliance execution signature sign-off actions
  const handleApproveRecord = async (recordId) => {
    try {
      // Aligned with the direct /ledger/ validation routing path
      const response = await fetch(`http://127.0.0.1:8000/ledger/${recordId}/approve-record/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      if (response.ok) {
        // Refresh UI state instantly upon database locking confirmation
        fetchLedgerData(filterStatus);
      } else {
        const errData = await response.json();
        alert(`Approval Denied: ${errData.error}`);
      }
    } catch (error) {
      alert(`Network communications error: ${error}`);
    }
  };

  // 3. Aggregate live chart data dynamically based on ledger metrics
  const chartData = [
    { name: 'Scope 1 (Direct)', CO2e: records.filter(r => r.scope_category === 'SCOPE_1').reduce((acc, r) => acc + parseFloat(r.normalized_quantity_co2e || 0), 0) },
    { name: 'Scope 2 (Grid)', CO2e: records.filter(r => r.scope_category === 'SCOPE_2').reduce((acc, r) => acc + parseFloat(r.normalized_quantity_co2e || 0), 0) },
    { name: 'Scope 3 (Value Chain)', CO2e: records.filter(r => r.scope_category === 'SCOPE_3').reduce((acc, r) => acc + parseFloat(r.normalized_quantity_co2e || 0), 0) },
  ];

  return (
    <div className="min-h-screen bg-gray-50 text-gray-800 font-sans">
      {/* Platform Global Top Header Banner */}
      <header className="bg-teal-900 text-white p-5 shadow-md flex justify-between items-center">
        <div className="flex items-center gap-3">
          <Activity className="h-8 w-8 text-teal-400" />
          <div>
            <h1 className="text-xl font-bold tracking-tight">BreatheESG Compliance Ledger</h1>
            <p className="text-xs text-teal-200">System Status: Secure Audit Execution Node Active</p>
          </div>
        </div>
        <div className="bg-teal-800 px-4 py-2 rounded text-sm font-mono border border-teal-700">
          Tenant Workspace ID: Acme_Corp_HQ
        </div>
      </header>

      <main className="p-6 max-w-7xl mx-auto grid grid-cols-1 gap-6">

        {/* Upper Dashboard Grid Section: Metric Totals vs Bar Chart */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-xl shadow-sm border border-gray-100 flex flex-col justify-between">
            <div>
              <p className="text-sm font-semibold text-gray-400 uppercase tracking-wider">Total Ledger Scope Footprint</p>
              <h3 className="text-4xl font-extrabold text-teal-950 mt-2">
                {records.reduce((acc, r) => acc + parseFloat(r.normalized_quantity_co2e || 0), 0).toFixed(2)}
                <span className="text-lg font-medium text-gray-500 ml-1">MT CO2e</span>
              </h3>
            </div>
            <div className="mt-4 text-xs text-gray-400 border-t pt-3">
              Aggregated across {records.length} streaming multi-source entries.
            </div>
          </div>

          <div className="bg-white p-5 rounded-xl shadow-sm border border-gray-100 md:col-span-2">
            <h4 className="text-sm font-bold text-gray-700 mb-3 uppercase tracking-wider">Carbon Burden Portfolio Analysis ({chartData.reduce((acc, d) => acc + d.CO2e, 0).toFixed(1)} MT total)</h4>
            <div className="h-40">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={chartData}>
                  <XAxis dataKey="name" fontSize={12} stroke="#6b7280" />
                  <YAxis fontSize={12} stroke="#6b7280" />
                  <Tooltip />
                  <Bar dataKey="CO2e" fill="#0f766e" radius={[4, 4, 0, 0]}>
                    {chartData.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={index === 0 ? '#14b8a6' : index === 1 ? '#0d9488' : '#115e59'} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Middle Control Filtering Interface Toolbar */}
        <div className="flex justify-between items-center bg-white p-4 rounded-xl shadow-sm border border-gray-100">
          <div className="flex items-center gap-2">
            <FileSpreadsheet className="text-teal-700 h-5 w-5" />
            <span className="font-bold text-gray-700 text-sm">Audit Data Stream Pipeline Filter:</span>
          </div>
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="border bg-gray-50 border-gray-200 text-gray-700 rounded-lg px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-teal-600 transition"
          >
            <option value="">Show All Ledger Entries</option>
            <option value="VALID">Show Verified Passed Entries</option>
            <option value="SUSPICIOUS">Show Anomaly Flags (Suspicious)</option>
            <option value="FAILED">Show Systemic Format Failures</option>
          </select>
        </div>

        {/* Lower Main Data Table Ledger Feed */}
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 overflow-hidden">
          {loading ? (
            <div className="p-12 text-center text-gray-400 font-medium animate-pulse">Querying cloud ledger endpoints...</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left border-collapse">
                <thead>
                  <tr className="bg-gray-50 text-gray-400 font-bold text-xs uppercase tracking-wider border-b border-gray-100">
                    <th className="p-4">GHG Allocation Category</th>
                    <th className="p-4">Original Upload Metric</th>
                    <th className="p-4">Calculated Footprint</th>
                    <th className="p-4">Pipeline Status Check</th>
                    <th className="p-4 text-right">Auditor Signature Handshake</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100 text-sm">
                  {records.map((record) => (
                    <tr key={record.id} className="hover:bg-slate-50 transition">
                      <td className="p-4 font-medium text-gray-900">
                        <span className="block text-xs font-semibold text-teal-700 uppercase tracking-tight">{record.scope_category}</span>
                        {record.ghg_mapping_category}
                      </td>
                      <td className="p-4 font-mono text-gray-600">
                        {parseFloat(record.original_quantity || 0).toLocaleString()} {record.original_unit}
                      </td>
                      <td className="p-4 font-extrabold text-slate-950 font-mono">
                        {parseFloat(record.normalized_quantity_co2e || 0).toFixed(4)} MT CO2e
                      </td>
                      <td className="p-4">
                        {record.validation_status === 'VALID' && (
                          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-50 text-emerald-700">
                            <CheckCircle className="h-3.5 w-3.5" /> Checked Passed
                          </span>
                        )}
                        {record.validation_status === 'SUSPICIOUS' && (
                          <span className="inline-flex flex-col gap-1 px-3 py-1.5 rounded-lg text-xs font-semibold bg-amber-50 text-amber-800 border border-amber-200">
                            <span className="flex items-center gap-1"><AlertTriangle className="h-3.5 w-3.5 text-amber-600" /> ANOMALY WARNING</span>
                            <span className="text-[10px] text-amber-600 font-normal">{record.validation_notes}</span>
                          </span>
                        )}
                        {record.validation_status === 'FAILED' && (
                          <span className="inline-flex flex-col gap-1 px-3 py-1.5 rounded-lg text-xs font-semibold bg-rose-50 text-rose-800 border border-rose-200">
                            <span className="flex items-center gap-1"><ShieldAlert className="h-3.5 w-3.5 text-rose-600" /> CORRUPT RECORD</span>
                            <span className="text-[10px] text-rose-600 font-normal">{record.validation_notes}</span>
                          </span>
                        )}
                      </td>
                      <td className="p-4 text-right">
                        {record.is_locked ? (
                          <span className="inline-flex items-center gap-1 bg-gray-100 text-gray-500 px-3 py-1.5 rounded-md font-mono text-xs font-semibold select-none ml-auto border">
                            <Lock className="h-3 w-3" /> SIGNED & LOCKED
                          </span>
                        ) : (
                          <button
                            onClick={() => handleApproveRecord(record.id)}
                            disabled={record.validation_status === 'FAILED'}
                            className={`px-4 py-1.5 rounded-md text-xs font-bold shadow-sm transition active:scale-95 ${
                              record.validation_status === 'FAILED'
                                ? 'bg-gray-100 text-gray-300 cursor-not-allowed'
                                : 'bg-teal-700 text-white hover:bg-teal-800 hover:shadow'
                            }`}
                          >
                            Sign-Off Compliance Lock
                          </button>
                        )}
                      </td>
                    </tr>
                  ))}
                  {records.length === 0 && (
                    <tr>
                      <td colSpan="5" className="p-8 text-center text-gray-400 font-medium">No system entries found for selected filter status criteria.</td>
                    </tr>
                  )}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </main>
    </div>
  );
}

export default App;