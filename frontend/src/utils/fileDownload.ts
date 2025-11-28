import JSZip from 'jszip';

/**
 * Download a single file
 */
export function downloadFile(filename: string, content: string) {
  const blob = new Blob([content], { type: 'text/plain;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

/**
 * Download multiple files as a ZIP archive
 */
export async function downloadAllFilesAsZip(
  files: Record<string, string>,
  zipFilename: string = 'scaffy-project.zip'
) {
  const zip = new JSZip();

  // Add each file to the zip
  Object.entries(files).forEach(([filename, content]) => {
    zip.file(filename, content);
  });

  // Generate the zip file
  const blob = await zip.generateAsync({ type: 'blob' });

  // Download the zip
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = zipFilename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}
