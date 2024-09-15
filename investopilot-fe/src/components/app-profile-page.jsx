import { useState, useEffect, setError } from 'react'
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import Link from 'next/link'
import { useRouter } from 'next/navigation'

import { signOut } from 'supertokens-auth-react/recipe/emailpassword'

export function ProfilePage() {
  const [apiKey, setApiKey] = useState('')
  const [logoutButtonState, setLogoutButtonState] = useState('Logout')
  const [hasOpenAIKey, setHasOpenAIKey] = useState(false)
  const router = useRouter()

  useEffect(() => {
    const checkOpenAIKey = async () => {
        try {
            const response = await fetch('http://localhost:8000/openai-key', {
                method: 'GET',
                credentials: 'include',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            const json = await response.json();
            if (json && json.key) {
              setHasOpenAIKey(true)
            }
        } catch (error) {
            console.log(error)
        }
    };
    checkOpenAIKey();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      const response = await fetch('http://localhost:8000/openai-key', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ key: apiKey })
      })

      if (response.ok) {
        const data = await response.json()
        console.log('API Key saved:', data)
        // setMessage('API Key saved successfully!')
      } else {
        const errorData = await response.json()
        // setMessage(`Error: ${errorData.message}`)
        console.error('Error saving API Key:', errorData)
      }
    } catch (error) {
      console.error('Error saving API Key:', error)
      // setMessage('An error occurred while saving the API Key.')
    }
    // Here you would typically save the API key securely, perhaps to a backend service
    console.log('API Key saved:', apiKey)
    // In a real app, you'd want to show a success message to the user
  }

  const handleLogout = async () => {
    setLogoutButtonState('Logging out...')
    await signOut()
    router.push('/auth')
  }

  return (
    (
      (
        <div className="container mx-auto p-4">
          <Card className="max-w-md mx-auto">
            <CardHeader>
              <CardTitle>Profile Settings</CardTitle>
              <CardDescription>Manage your account and API key</CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSubmit} className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="api-key">GPT-4 API Key</Label>
                  <Input
                    id="api-key"
                    type="password"
                    value={apiKey}
                    onChange={(e) => setApiKey(e.target.value)}
                    placeholder="Enter your GPT-4 API key" />
                </div>
                <Button type="submit">{hasOpenAIKey ? "Update API Key" : "Save API Key"}</Button>
              </form>
              <div className="mt-6 space-y-4">
                <Link href="/dashboard">
                  <Button variant="outline" className="w-full">Back to Dashboard</Button>
                </Link>
                <Button variant="destructive" className="w-full" onClick={handleLogout}>
                  {logoutButtonState}
                </Button>
              </div>
            </CardContent>
          </Card>
        </div>)
    )
  );
}