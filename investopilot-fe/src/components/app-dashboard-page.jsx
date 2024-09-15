import { useState, useEffect } from 'react'
import { useRouter } from 'next/router'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { ArrowUpIcon, ArrowDownIcon, NewspaperIcon, Settings, Upload, Loader2 } from 'lucide-react'
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts'
import Link from 'next/link'

// Generate mock data for price history
const generateMockPriceHistory = () => {
  const data = []
  let price = 100
  for (let i = 30; i > 0; i--) {
    price += Math.random() * 10 - 5
    data.push({
      date: `2023-${(12 - Math.floor(i / 30)).toString().padStart(2, '0')}-${(30 - i % 30).toString().padStart(2, '0')}`,
      price: Math.max(0, price.toFixed(2))
    })
  }
  return data
}

export function DashboardPage() {
  const router = useRouter()
  const [watchlist, setWatchlist] = useState([])
  const [newStock, setNewStock] = useState('')
  const [uploadedDocs, setUploadedDocs] = useState([])
  const [showSuccessModal, setShowSuccessModal] = useState(false)
  const [uploadedFileName, setUploadedFileName] = useState('')
  const [stockInput, setStockInput] = useState('')
  const [isUploading, setIsUploading] = useState(false)

  const handleNavigation = () => {
    router.push('/profile')
  }

  useEffect(() => {
    // Initialize watchlist with mock data
    const initialStocks = [
      { symbol: 'NVDA', name: 'NVIDIA Corporation', pricePredict: 'up', newsPredict: 'up', latestNews: 'NVIDIA announces new GPU', priceHistory: generateMockPriceHistory() },
      { symbol: 'AAPL', name: 'Apple Inc.', pricePredict: 'up', newsPredict: 'down', latestNews: 'Apple announces new iPhone', priceHistory: generateMockPriceHistory() },
      { symbol: 'GOOGL', name: 'Alphabet Inc.', pricePredict: 'down', newsPredict: 'up', latestNews: 'Google launches new AI product', priceHistory: generateMockPriceHistory() },
      { symbol: 'MSFT', name: 'Microsoft Corporation', pricePredict: 'up', newsPredict: 'up', latestNews: 'Microsoft cloud services see record growth', priceHistory: generateMockPriceHistory() },
    ]
    setWatchlist(initialStocks)
  }, [])

  const handleAddStocks = async () => {
    // Split the input by commas and trim whitespace
    const stocksToAdd = stockInput.split(',').map(stock => stock.trim().toUpperCase()).filter(Boolean)

    // Limit to 5 stocks
    const limitedStocks = stocksToAdd.slice(0, 5)

    try {
      const response = await fetch('http://localhost:8000/stocks', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ stocks: limitedStocks }),
        credentials: 'include',
      })
      if (response.ok) {
        // Update the watchlist with the new stocks
        setWatchlist(limitedStocks.map(symbol => ({ 
          symbol, 
          name: symbol, 
          pricePredict: 'up', 
          newsPredict: 'up', 
          latestNews: 'No recent news', 
          priceHistory: generateMockPriceHistory() 
        })))
        setStockInput('') // Clear the input
      } else {
        console.error('Failed to save stocks')
        // You might want to show an error message to the user here
      }
    } catch (error) {
      console.error('Error saving stocks:', error)
      // You might want to show an error message to the user here
    }
  }

  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (file && file.type === 'application/pdf') {
      const formData = new FormData();
      formData.append('file', file);
      formData.append('filing_type', '10-K'); // or '10-Q', depending on your use case

      setIsUploading(true);

      try {
        const response = await fetch('http://localhost:8000/upload-file', {
          method: 'POST',
          credentials: 'include',
          body: formData,
        });

        const result = await response.json();

        if (response.ok) {
          // Add the uploaded file to the list
          const newDoc = {
            name: file.name,
            type: file.type,
            size: file.size,
            uploadDate: new Date().toISOString()
          };
          setUploadedDocs(prevDocs => [...prevDocs, newDoc]);

          // Show success modal
          setUploadedFileName(file.name);
          setShowSuccessModal(true);
          setTimeout(() => setShowSuccessModal(false), 2000);
        } else {
          console.error('File upload failed:', result.message);
          console.error('Error type:', result.error_type);
          // You might want to show this error to the user
          alert(`File upload failed: ${result.message}`);
        }
      } catch (error) {
        console.error('Error uploading file:', error);
        alert('An error occurred while uploading the file. Please try again.');
      } finally {
        setIsUploading(false);
      }
    } else {
      console.error('Please select a PDF file');
      alert('Please select a PDF file');
    }
  }

  return (
    <>
      <div className="container mx-auto p-4">
        <div className="flex justify-between items-center mb-4">
          <h1 className="text-2xl font-bold">Stock Watchlist Dashboard</h1>
          <Button variant="outline" size="icon" onClick={handleNavigation}>
            <Settings className="h-4 w-4" />
          </Button>
        </div>
        <div className="mb-4">
          <Input
            value={stockInput}
            onChange={(e) => setStockInput(e.target.value)}
            placeholder="Enter stock symbols (comma-separated, max 5)"
            className="mb-2"
          />
          <Button 
            onClick={handleAddStocks} 
            disabled={!stockInput.trim()}
            className="w-full"
          >
            Add Stocks
          </Button>
        </div>
        {/* Document Upload Section */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>Upload Financial Documents</CardTitle>
            <CardDescription>Upload 10-K, 10-Q, or related financial articles</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-2">
              <Input
                type="file"
                multiple
                id="fileInput"
                accept=".pdf,.doc,.docx,.xls,.xlsx"
                className="flex-grow"
                disabled={isUploading}
              />
              <Button 
                onClick={() => {
                  const fileInput = document.getElementById('fileInput');
                  if (fileInput.files.length > 0) {
                    const file = fileInput.files[0];
                    const formData = new FormData();
                    formData.append('file', file);
                    handleFileUpload({ target: { files: [file] } });
                  } else {
                    console.error('No file selected');
                  }
                }}
                disabled={isUploading}
              >
                {isUploading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Uploading
                  </>
                ) : (
                  <>
                    <Upload className="mr-2 h-4 w-4" /> Upload
                  </>
                )}
              </Button>
            </div>
            {uploadedDocs.length > 0 && (
              <div className="mt-4">
                <h3 className="font-semibold mb-2">Uploaded Documents:</h3>
                <ul className="list-disc pl-5">
                  {uploadedDocs.map((doc, index) => (
                    <li key={index}>
                      {doc.name} ({(doc.size / 1024).toFixed(2)} KB)
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </CardContent>
        </Card>
        {/* Watchlist Section */}
        <div className="grid grid-cols-1 gap-4">
          {watchlist.map((stock) => (
            <Card key={stock.symbol} className="w-full">
              <CardHeader>
                <CardTitle>{stock.symbol}</CardTitle>
                <CardDescription>{stock.name}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="flex flex-col md:flex-row">
                  <div className="w-full md:w-1/2 h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={stock.priceHistory}>
                        <XAxis
                          dataKey="date"
                          tick={{fontSize: 12}}
                          tickFormatter={(tick) => new Date(tick).toLocaleDateString()} />
                        <YAxis tick={{fontSize: 12}} domain={['auto', 'auto']} />
                        <Tooltip
                          labelFormatter={(label) => new Date(label).toLocaleDateString()}
                          formatter={(value) => [`$${value}`, 'Price']} />
                        <Line
                          type="monotone"
                          dataKey="price"
                          stroke="#8884d8"
                          dot={false}
                          strokeWidth={2} />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                  <div className="w-full md:w-1/2 pl-0 md:pl-4 mt-4 md:mt-0">
                    <div className="flex justify-between mb-2">
                      <span>Price Prediction:</span>
                      {stock.pricePredict === 'up' ? <ArrowUpIcon className="text-green-500" /> : <ArrowDownIcon className="text-red-500" />}
                    </div>
                    <div className="flex justify-between mb-2">
                      <span>News Prediction:</span>
                      {stock.newsPredict === 'up' ? <ArrowUpIcon className="text-green-500" /> : <ArrowDownIcon className="text-red-500" />}
                    </div>
                    <div className="flex items-center mt-4">
                      <NewspaperIcon className="mr-2" />
                      <span className="text-sm">{stock.latestNews}</span>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
      {showSuccessModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-xl">
            <h2 className="text-xl font-bold mb-4">Upload Successful</h2>
            <p className="mb-4">{uploadedFileName} has been uploaded.</p>
            <button
              className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
              onClick={() => setShowSuccessModal(false)}
            >
              Close
            </button>
          </div>
        </div>
      )}
    </>
  );
}