"use client"

import { AppSidebar } from "@/components/app-sidebar"
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbPage,
  BreadcrumbSeparator,
} from "@/components/ui/breadcrumb"
import { Separator } from "@/components/ui/separator"
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Bot, Shield, Clock, Zap, AlertCircle, TrendingUp } from "lucide-react"

export default function Page() {
  return (
    <SidebarProvider>
      <AppSidebar activePage="vincent" />
      <SidebarInset>
        <header className="flex h-16 shrink-0 items-center gap-2 transition-[width,height] ease-linear group-has-data-[collapsible=icon]/sidebar-wrapper:h-12">
          <div className="flex items-center gap-2 px-4">
            <SidebarTrigger className="-ml-1" />
            <Separator
              orientation="vertical"
              className="mr-2 data-[orientation=vertical]:h-4"
            />
            <Breadcrumb>
              <BreadcrumbList>
                <BreadcrumbItem>
                  <BreadcrumbLink href="/dashboard">Kairos</BreadcrumbLink>
                </BreadcrumbItem>
                <BreadcrumbSeparator className="hidden md:block" />
                <BreadcrumbItem>
                  <BreadcrumbPage>Vincent Police</BreadcrumbPage>
                </BreadcrumbItem>
              </BreadcrumbList>
            </Breadcrumb>
          </div>
        </header>
        <div className="flex flex-1 flex-col gap-4 p-4 pt-0">
          {/* Coming Soon Card */}
          <Card className="border-2 border-dashed">
            <CardHeader className="text-center">
              <div className="flex justify-center mb-4">
                <div className="relative">
                  <Bot className="h-16 w-16 text-primary" />
                  <Shield className="h-8 w-8 text-blue-600 absolute -bottom-1 -right-1" />
                </div>
              </div>
              <CardTitle className="text-3xl font-bold">Vincent Police Integration Coming Soon</CardTitle>
              <Badge variant="secondary" className="mt-2">In Development</Badge>
              <CardDescription className="mt-4 text-lg">
                Protect your DeFi investments with Vincent's AI-powered security monitoring
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-6">
              {/* What is Vincent */}
              <div className="space-y-4">
                <h3 className="text-xl font-semibold">What is Vincent?</h3>
                <p className="text-muted-foreground">
                  Vincent is an AI agent that monitors your blockchain transactions and DeFi activities in real-time. 
                  It acts as your personal security guard, detecting suspicious patterns, warning about potential scams, 
                  and helping you make safer investment decisions in the crypto space.
                </p>
              </div>

              {/* Key Features */}
              <div className="grid gap-4 md:grid-cols-2">
                <Card className="bg-muted/50">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-lg">
                      <AlertCircle className="h-5 w-5 text-yellow-600" />
                      Scam Detection
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground">
                      Real-time analysis of smart contracts and transactions to identify potential rugpulls, 
                      honeypots, and malicious contracts before you interact with them.
                    </p>
                  </CardContent>
                </Card>

                <Card className="bg-muted/50">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-lg">
                      <Shield className="h-5 w-5 text-blue-600" />
                      Transaction Monitoring
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground">
                      24/7 monitoring of your wallet activities with instant alerts for unusual patterns, 
                      unauthorized access attempts, or suspicious approvals.
                    </p>
                  </CardContent>
                </Card>

                <Card className="bg-muted/50">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-lg">
                      <Zap className="h-5 w-5 text-purple-600" />
                      Risk Assessment
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground">
                      Automated risk scoring for DeFi protocols, liquidity pools, and yield farming opportunities 
                      to help you make informed investment decisions.
                    </p>
                  </CardContent>
                </Card>

                <Card className="bg-muted/50">
                  <CardHeader>
                    <CardTitle className="flex items-center gap-2 text-lg">
                      <TrendingUp className="h-5 w-5 text-green-600" />
                      Portfolio Protection
                    </CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-muted-foreground">
                      Smart recommendations for portfolio diversification and exposure limits to minimize 
                      risks while maximizing your DeFi yields.
                    </p>
                  </CardContent>
                </Card>
              </div>

              {/* Integration Benefits */}
              <div className="bg-primary/5 rounded-lg p-6 space-y-3">
                <h3 className="text-lg font-semibold">Vincent + Kairos Integration Benefits</h3>
                <ul className="space-y-2 text-sm text-muted-foreground">
                  <li className="flex items-start gap-2">
                    <Clock className="h-4 w-4 mt-0.5 text-primary" />
                    <span>Pre-trade security checks before Kairos executes any autonomous trades</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <Shield className="h-4 w-4 mt-0.5 text-primary" />
                    <span>Real-time monitoring of all AI agent activities for enhanced safety</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <AlertCircle className="h-4 w-4 mt-0.5 text-primary" />
                    <span>Instant alerts if any suspicious patterns are detected in your trading</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <Bot className="h-4 w-4 mt-0.5 text-primary" />
                    <span>AI-powered security recommendations tailored to your trading strategy</span>
                  </li>
                </ul>
              </div>

              {/* Coming Soon Notice */}
              <div className="text-center pt-6 space-y-2">
                <p className="text-lg font-medium">🚀 Launching Soon</p>
                <p className="text-muted-foreground">
                  We're working on seamlessly integrating Vincent's security features into Kairos 
                  to provide you with the safest autonomous trading experience.
                </p>
              </div>
            </CardContent>
          </Card>
        </div>
      </SidebarInset>
    </SidebarProvider>
  )
}