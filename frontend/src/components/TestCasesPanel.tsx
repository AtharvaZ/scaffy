import { useState, useEffect } from 'react';
import { ChevronDown, ChevronRight, TestTube2, Edit2, Trash2, Plus, Save, X, Check } from 'lucide-react';
import { Button } from './ui/button';
import type { TestCase, TestResult } from '../types';

interface TestCasesPanelProps {
  testCases: TestCase[];
  onTestCasesChange?: (testCases: TestCase[]) => void;
  testResults?: TestResult[];
}

export function TestCasesPanel({ testCases, onTestCasesChange, testResults }: TestCasesPanelProps) {
  const [expandedTest, setExpandedTest] = useState<string | null>(null);
  const [editingTest, setEditingTest] = useState<number | null>(null);
  const [editedTests, setEditedTests] = useState<TestCase[]>(testCases);

  // Sync editedTests with testCases prop when it changes (e.g., after generating new tests)
  useEffect(() => {
    console.log("🔄 TestCasesPanel: testCases prop changed, updating editedTests");
    console.log("  - New testCases length:", testCases.length);
    setEditedTests(testCases);
  }, [testCases]);

  const hasTests = testCases && testCases.length > 0;

  // Helper function to get test result for a test case
  const getTestResult = (testName: string): TestResult | undefined => {
    return testResults?.find(result => result.test_name === testName);
  };

  const handleEdit = (index: number, testKey: string) => {
    setEditingTest(index);
    setEditedTests([...testCases]);
    // Expand the test case if not already expanded
    if (expandedTest !== testKey) {
      setExpandedTest(testKey);
    }
  };

  const handleSave = () => {
    if (onTestCasesChange) {
      onTestCasesChange(editedTests);
    }
    setEditingTest(null);
  };

  const handleCancel = () => {
    setEditedTests([...testCases]);
    setEditingTest(null);
  };

  const handleDelete = (index: number) => {
    const newTests = testCases.filter((_, i) => i !== index);
    if (onTestCasesChange) {
      onTestCasesChange(newTests);
    }
  };

  const handleFieldChange = (index: number, field: keyof TestCase, value: string) => {
    const newTests = [...editedTests];
    newTests[index] = { ...newTests[index], [field]: value };
    setEditedTests(newTests);
  };

  const handleAddTest = () => {
    const newTest: TestCase = {
      test_name: 'test_new',
      function_name: '',
      input_data: '',
      expected_output: '',
      description: 'New test case',
      test_type: 'normal',
    };
    const newTests = [...testCases, newTest];
    if (onTestCasesChange) {
      onTestCasesChange(newTests);
    }
    // Expand the new test
    setExpandedTest(`${newTest.test_name}-${newTests.length - 1}`);
  };

  return (
    <div className="h-full flex flex-col bg-white dark:bg-black border border-gray-200/60 dark:border-gray-800/60 rounded-lg overflow-hidden">
      {/* Header */}
      <div className="flex-shrink-0 p-4 border-b border-gray-200/60 dark:border-gray-800/60 bg-gray-50/50 dark:bg-gray-900/30">
        <div className="flex items-center gap-2">
          <TestTube2 className="h-4 w-4 text-blue-600 dark:text-blue-400" />
          <h3 className="text-base font-semibold text-black dark:text-white">
            Test Cases
          </h3>
          <span className="ml-auto text-sm text-gray-600 dark:text-gray-400">
            {hasTests ? `${testCases.length} ${testCases.length === 1 ? 'test' : 'tests'}` : 'No tests'}
          </span>
          {hasTests && (
            <Button
              onClick={handleAddTest}
              size="sm"
              variant="outline"
              className="ml-2 h-6 px-2 text-xs"
            >
              <Plus className="h-3 w-3 mr-1" />
              Add Test
            </Button>
          )}
        </div>
      </div>

      {/* Test Cases List */}
      <div className="flex-1 overflow-y-auto">
        {!hasTests ? (
          <div className="flex flex-col items-center justify-center h-full p-8 text-center">
            <TestTube2 className="h-12 w-12 text-gray-400 dark:text-gray-600 mb-4" />
            <p className="text-sm text-gray-600 dark:text-gray-400">
              No test cases available
            </p>
          </div>
        ) : (
          testCases.map((test, index) => {
          const testKey = `${test.test_name}-${index}`;
          const isExpanded = expandedTest === testKey;
          const isEditing = editingTest === index;
          const currentTest = isEditing ? editedTests[index] : test;

          // Determine test type color
          const typeColor =
            currentTest.test_type === 'normal'
              ? 'text-blue-600 dark:text-blue-400'
              : currentTest.test_type === 'edge'
              ? 'text-yellow-600 dark:text-yellow-400'
              : 'text-red-600 dark:text-red-400';

          return (
            <div
              key={testKey}
              className="border-b border-gray-200/60 dark:border-gray-800/60 last:border-b-0"
            >
              {/* Test case header */}
              <div className="w-full flex items-center gap-2 p-3 hover:bg-gray-50 dark:hover:bg-gray-900/50 transition-colors">
                <button
                  onClick={() => setExpandedTest(isExpanded ? null : testKey)}
                  className="flex-1 flex items-center gap-3 text-left"
                >
                  {/* Expand/Collapse icon */}
                  {isExpanded ? (
                    <ChevronDown className="h-4 w-4 text-gray-400 flex-shrink-0" />
                  ) : (
                    <ChevronRight className="h-4 w-4 text-gray-400 flex-shrink-0" />
                  )}

                  {/* Pass/Fail indicator */}
                  {(() => {
                    const result = getTestResult(currentTest.test_name);
                    if (result) {
                      return (
                        <div className={`flex-shrink-0 w-5 h-5 rounded-full flex items-center justify-center ${
                          result.passed
                            ? 'bg-green-100 dark:bg-green-900/30'
                            : 'bg-red-100 dark:bg-red-900/30'
                        }`}>
                          {result.passed ? (
                            <Check className="h-3 w-3 text-green-600 dark:text-green-400" />
                          ) : (
                            <X className="h-3 w-3 text-red-600 dark:text-red-400" />
                          )}
                        </div>
                      );
                    }
                    return null;
                  })()}

                  {/* Test name */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="text-base font-medium text-black dark:text-white truncate">
                        {currentTest.test_name}
                      </span>
                      <span className={`text-sm font-medium ${typeColor} uppercase`}>
                        {currentTest.test_type}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mt-0.5 line-clamp-1">
                      {currentTest.description}
                    </p>
                  </div>
                </button>

                {/* Action buttons */}
                {!isEditing ? (
                  <div className="flex items-center gap-1">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleEdit(index, testKey);
                      }}
                      className="p-1 hover:bg-gray-200 dark:hover:bg-gray-800 rounded"
                      title="Edit test"
                    >
                      <Edit2 className="h-3 w-3 text-gray-600 dark:text-gray-400" />
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleDelete(index);
                      }}
                      className="p-1 hover:bg-red-100 dark:hover:bg-red-900/30 rounded"
                      title="Delete test"
                    >
                      <Trash2 className="h-3 w-3 text-red-600 dark:text-red-400" />
                    </button>
                  </div>
                ) : (
                  <div className="flex items-center gap-1">
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleSave();
                      }}
                      className="p-1 hover:bg-green-100 dark:hover:bg-green-900/30 rounded"
                      title="Save changes"
                    >
                      <Save className="h-3 w-3 text-green-600 dark:text-green-400" />
                    </button>
                    <button
                      onClick={(e) => {
                        e.stopPropagation();
                        handleCancel();
                      }}
                      className="p-1 hover:bg-gray-200 dark:hover:bg-gray-800 rounded"
                      title="Cancel"
                    >
                      <X className="h-3 w-3 text-gray-600 dark:text-gray-400" />
                    </button>
                  </div>
                )}
              </div>

              {/* Expanded test details */}
              {isExpanded && (
                <div className="px-3 pb-3 space-y-3 bg-gray-50/50 dark:bg-gray-900/30">
                  {/* Test Name */}
                  <div>
                    <div className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">
                      Test Name:
                    </div>
                    {isEditing ? (
                      <input
                        type="text"
                        value={currentTest.test_name}
                        onChange={(e) => handleFieldChange(index, 'test_name', e.target.value)}
                        className="block w-full text-sm bg-white dark:bg-black px-2 py-1 rounded border border-gray-200 dark:border-gray-800 text-gray-800 dark:text-gray-300 font-mono"
                      />
                    ) : (
                      <code className="block text-sm bg-white dark:bg-black px-2 py-1 rounded border border-gray-200 dark:border-gray-800 text-gray-800 dark:text-gray-300 font-mono">
                        {currentTest.test_name}
                      </code>
                    )}
                  </div>

                  {/* Function name */}
                  <div>
                    <div className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">
                      Function:
                    </div>
                    {isEditing ? (
                      <input
                        type="text"
                        value={currentTest.function_name}
                        onChange={(e) => handleFieldChange(index, 'function_name', e.target.value)}
                        className="block w-full text-sm bg-white dark:bg-black px-2 py-1 rounded border border-gray-200 dark:border-gray-800 text-gray-800 dark:text-gray-300 font-mono"
                      />
                    ) : (
                      <code className="block text-sm bg-white dark:bg-black px-2 py-1 rounded border border-gray-200 dark:border-gray-800 text-gray-800 dark:text-gray-300 font-mono">
                        {currentTest.function_name}
                      </code>
                    )}
                  </div>

                  {/* Description */}
                  <div>
                    <div className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">
                      Description:
                    </div>
                    {isEditing ? (
                      <textarea
                        value={currentTest.description}
                        onChange={(e) => handleFieldChange(index, 'description', e.target.value)}
                        rows={2}
                        className="block w-full text-sm bg-white dark:bg-black px-2 py-1 rounded border border-gray-200 dark:border-gray-800 text-gray-800 dark:text-gray-300"
                      />
                    ) : (
                      <p className="text-sm text-gray-700 dark:text-gray-300 px-2 py-1">
                        {currentTest.description}
                      </p>
                    )}
                  </div>

                  {/* Input */}
                  <div>
                    <div className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">
                      Input:
                    </div>
                    {isEditing ? (
                      <textarea
                        value={currentTest.input_data}
                        onChange={(e) => handleFieldChange(index, 'input_data', e.target.value)}
                        rows={3}
                        className="block w-full text-sm bg-white dark:bg-black px-2 py-1 rounded border border-gray-200 dark:border-gray-800 text-gray-800 dark:text-gray-300 font-mono"
                      />
                    ) : (
                      <code className="block text-sm bg-white dark:bg-black px-2 py-1 rounded border border-gray-200 dark:border-gray-800 text-gray-800 dark:text-gray-300 font-mono whitespace-pre-wrap">
                        {currentTest.input_data}
                      </code>
                    )}
                  </div>

                  {/* Expected Output */}
                  <div>
                    <div className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">
                      Expected Output:
                    </div>
                    {isEditing ? (
                      <textarea
                        value={currentTest.expected_output}
                        onChange={(e) => handleFieldChange(index, 'expected_output', e.target.value)}
                        rows={3}
                        className="block w-full text-sm bg-white dark:bg-black px-2 py-1 rounded border border-gray-200 dark:border-gray-800 text-gray-800 dark:text-gray-300 font-mono"
                      />
                    ) : (
                      <code className="block text-sm bg-white dark:bg-black px-2 py-1 rounded border border-gray-200 dark:border-gray-800 text-gray-800 dark:text-gray-300 font-mono whitespace-pre-wrap">
                        {currentTest.expected_output}
                      </code>
                    )}
                  </div>

                  {/* Test Type */}
                  <div>
                    <div className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-1">
                      Test Type:
                    </div>
                    {isEditing ? (
                      <select
                        value={currentTest.test_type}
                        onChange={(e) => handleFieldChange(index, 'test_type', e.target.value)}
                        className="block text-sm bg-white dark:bg-black px-2 py-1 rounded border border-gray-200 dark:border-gray-800 text-gray-800 dark:text-gray-300"
                      >
                        <option value="normal">Normal Case</option>
                        <option value="edge">Edge Case</option>
                        <option value="error">Error Case</option>
                      </select>
                    ) : (
                      <span className={`inline-block text-sm font-medium px-2 py-1 rounded ${
                        currentTest.test_type === 'normal'
                          ? 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300'
                          : currentTest.test_type === 'edge'
                          ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300'
                          : 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300'
                      }`}>
                        {currentTest.test_type === 'normal' ? 'Normal Case' : currentTest.test_type === 'edge' ? 'Edge Case' : 'Error Case'}
                      </span>
                    )}
                  </div>
                </div>
              )}
            </div>
          );
        })
        )}
      </div>
    </div>
  );
}
