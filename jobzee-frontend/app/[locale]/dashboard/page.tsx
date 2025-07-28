"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuthStore } from "../../../lib/auth-store";
import { Header } from "../../../components/layout/Header";
import { Footer } from "../../../components/layout/Footer";
import { Card } from "../../../components/ui/Card";
import { Button } from "../../../components/ui/Button";
import {
  Briefcase,
  User,
  Bell,
  Settings,
  TrendingUp,
  Calendar,
  MapPin,
  DollarSign,
} from "lucide-react";

export default function DashboardPage() {
  const router = useRouter();
  const { user, isAuthenticated, isLoading } = useAuthStore();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push("/auth/login");
    }
  }, [isAuthenticated, isLoading, router]);

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  const stats = [
    {
      title: "Active Applications",
      value: "12",
      change: "+2",
      icon: Briefcase,
      color: "bg-blue-100 text-blue-600",
    },
    {
      title: "Profile Views",
      value: "48",
      change: "+12",
      icon: User,
      color: "bg-green-100 text-green-600",
    },
    {
      title: "New Messages",
      value: "3",
      change: "+1",
      icon: Bell,
      color: "bg-yellow-100 text-yellow-600",
    },
    {
      title: "Match Score",
      value: "95%",
      change: "+5%",
      icon: TrendingUp,
      color: "bg-purple-100 text-purple-600",
    },
  ];

  const recentJobs = [
    {
      id: 1,
      title: "Senior Frontend Developer",
      company: "TechCorp Inc.",
      location: "San Francisco, CA",
      salary: "$120k - $150k",
      posted: "2 days ago",
      matchScore: 95,
    },
    {
      id: 2,
      title: "Full Stack Engineer",
      company: "StartupXYZ",
      location: "Remote",
      salary: "$100k - $130k",
      posted: "3 days ago",
      matchScore: 88,
    },
    {
      id: 3,
      title: "React Developer",
      company: "Digital Solutions",
      location: "New York, NY",
      salary: "$90k - $120k",
      posted: "1 week ago",
      matchScore: 82,
    },
  ];

  return (
    <>
      <Header />
      <main className="pt-16 min-h-screen bg-gray-50">
        <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Welcome Section */}
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Welcome back, {user?.firstName}!
            </h1>
            <p className="text-gray-600">
              Here's what's happening with your job search today.
            </p>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            {stats.map((stat, index) => (
              <Card key={index} className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-sm font-medium text-gray-600">
                      {stat.title}
                    </p>
                    <p className="text-2xl font-bold text-gray-900">
                      {stat.value}
                    </p>
                    <p className="text-sm text-green-600">
                      {stat.change} from last week
                    </p>
                  </div>
                  <div
                    className={`w-12 h-12 ${stat.color} rounded-lg flex items-center justify-center`}
                  >
                    <stat.icon className="w-6 h-6" />
                  </div>
                </div>
              </Card>
            ))}
          </div>

          {/* Main Content Grid */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Recommended Jobs */}
            <div className="lg:col-span-2">
              <Card>
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-xl font-semibold text-gray-900">
                    Recommended Jobs
                  </h2>
                  <Button variant="outline" size="sm">
                    View All
                  </Button>
                </div>
                <div className="space-y-4">
                  {recentJobs.map((job) => (
                    <div
                      key={job.id}
                      className="p-4 border border-gray-200 rounded-lg hover:border-blue-300 transition-colors"
                    >
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h3 className="font-semibold text-gray-900 mb-1">
                            {job.title}
                          </h3>
                          <p className="text-gray-600 mb-2">{job.company}</p>
                          <div className="flex items-center space-x-4 text-sm text-gray-500">
                            <div className="flex items-center">
                              <MapPin className="w-4 h-4 mr-1" />
                              {job.location}
                            </div>
                            <div className="flex items-center">
                              <DollarSign className="w-4 h-4 mr-1" />
                              {job.salary}
                            </div>
                            <div className="flex items-center">
                              <Calendar className="w-4 h-4 mr-1" />
                              {job.posted}
                            </div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className="text-sm font-medium text-green-600 mb-1">
                            {job.matchScore}% match
                          </div>
                          <Button variant="primary" size="sm">
                            Apply
                          </Button>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            </div>

            {/* Sidebar */}
            <div className="space-y-6">
              {/* Quick Actions */}
              <Card>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Quick Actions
                </h3>
                <div className="space-y-3">
                  <Button variant="outline" fullWidth className="justify-start">
                    <Briefcase className="w-4 h-4 mr-2" />
                    Update Profile
                  </Button>
                  <Button variant="outline" fullWidth className="justify-start">
                    <Bell className="w-4 h-4 mr-2" />
                    Job Alerts
                  </Button>
                  <Button variant="outline" fullWidth className="justify-start">
                    <Settings className="w-4 h-4 mr-2" />
                    Preferences
                  </Button>
                </div>
              </Card>

              {/* Profile Completion */}
              <Card>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  Profile Completion
                </h3>
                <div className="mb-4">
                  <div className="flex justify-between text-sm mb-2">
                    <span>Profile Strength</span>
                    <span>85%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-blue-600 h-2 rounded-full"
                      style={{ width: "85%" }}
                    ></div>
                  </div>
                </div>
                <div className="space-y-2 text-sm">
                  <div className="flex items-center text-green-600">
                    <div className="w-2 h-2 bg-green-600 rounded-full mr-2"></div>
                    Basic Information
                  </div>
                  <div className="flex items-center text-green-600">
                    <div className="w-2 h-2 bg-green-600 rounded-full mr-2"></div>
                    Work Experience
                  </div>
                  <div className="flex items-center text-yellow-600">
                    <div className="w-2 h-2 bg-yellow-600 rounded-full mr-2"></div>
                    Skills & Certifications
                  </div>
                  <div className="flex items-center text-red-600">
                    <div className="w-2 h-2 bg-red-600 rounded-full mr-2"></div>
                    Portfolio/Projects
                  </div>
                </div>
              </Card>
            </div>
          </div>
        </div>
      </main>
      <Footer />
    </>
  );
}
