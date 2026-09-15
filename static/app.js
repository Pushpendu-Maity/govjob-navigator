/**
 * app.js - GovJob Navigator Frontend State & Controller
 * Powers reactive state, instant eligibility calculation, deadlines, AI counselor, and bookmarks.
 */

document.addEventListener('alpine:init', () => {
  Alpine.data('govJobApp', () => ({
    // Navigation
    currentTab: 'finder', // 'finder' | 'deadlines' | 'browse' | 'ai' | 'bookmarks'
    
    // User Profile for Eligibility Assessment
    profile: {
      dob: '2002-06-15',
      age: 24,
      category: 'UR',
      is_pwd: false,
      is_ex_serviceman: false,
      gender: 'male',
      domicile: 'All-India',
      education_level: 'graduate',
      stream: 'any',
      percentage: 65,
      check_physical: false,
      height_cm: 172
    },

    // Eligibility Assessment State
    isAssessing: false,
    hasAssessed: false,
    assessmentResults: {
      summary: {
        eligible_count: 0,
        near_match_count: 0,
        ineligible_count: 0,
        total_vacancies: 0
      },
      eligible: [],
      near_match: [],
      ineligible: []
    },
    activeResultTab: 'eligible', // 'eligible' | 'near_match' | 'ineligible'

    // Deadlines State
    deadlines: [],
    deadlineFilter: 'all', // 'all' | 'closing_soon' | 'open' | 'upcoming'
    isLoadingDeadlines: false,

    // Browse Catalog State
    catalogJobs: [],
    isLoadingCatalog: false,
    searchQuery: '',
    selectedTier: '',
    selectedSector: '',
    selectedStatus: '',
    selectedEdu: '',
    sortBy: 'status',

    // Modal Details
    activeJobModal: null,
    
    // Alerts Subscription
    showAlertModal: false,
    alertContact: '',
    alertSubmitted: false,
    alertMsg: '',

    // AI Counselor Chat
    aiQuery: '',
    isAiTyping: false,
    chatHistory: [
      {
        sender: 'ai',
        title: 'Namaste! Welcome to GovJob Navigator AI Counselor',
        text: 'I can help you explore government exams, compare career trajectories (e.g. SSC CGL vs Bank PO), understand 7th CPC pay scales, or find jobs that require **no written exam (direct merit)**. How can I assist you today?',
        actions: ['High salary 10th pass jobs', 'Direct merit jobs', 'SSC CGL vs Bank PO', '7th CPC Salary Structure']
      }
    ],

    // Bookmarks (LocalStorage)
    bookmarkedIds: [],

    // Init Hook
    init() {
      // Load saved bookmarks
      try {
        const saved = localStorage.getItem('govjob_bookmarks');
        if (saved) {
          this.bookmarkedIds = JSON.parse(saved);
        }
      } catch (e) {
        this.bookmarkedIds = [];
      }

      // Initial DOB age calculation
      this.updateAgeFromDob();

      // Auto-load catalog & deadlines
      this.fetchCatalog();
      this.fetchDeadlines();

      // Trigger automatic initial eligibility check so the user immediately sees live data!
      this.runEligibilityCheck(false);
    },

    // Age Calculation Helper
    updateAgeFromDob() {
      if (!this.profile.dob) return;
      const birthDate = new Date(this.profile.dob);
      const cutoffDate = new Date('2026-08-01'); // Standard reference
      let age = cutoffDate.getFullYear() - birthDate.getFullYear();
      const m = cutoffDate.getMonth() - birthDate.getMonth();
      if (m < 0 || (m === 0 && cutoffDate.getDate() < birthDate.getDate())) {
        age--;
      }
      this.profile.age = Math.max(16, age);
    },

    // Eligibility Assessment
    async runEligibilityCheck(showConfetti = true) {
      this.isAssessing = true;
      try {
        const res = await fetch('/api/check-eligibility', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this.profile)
        });
        const data = await res.json();
        if (data.success) {
          this.assessmentResults = data;
          this.hasAssessed = true;
          this.activeResultTab = data.summary.eligible_count > 0 ? 'eligible' : 'near_match';

          // Trigger confetti if eligible jobs found and user triggered
          if (showConfetti && data.summary.eligible_count > 0 && window.confetti) {
            window.confetti({
              particleCount: 60,
              spread: 70,
              origin: { y: 0.6 }
            });
          }
        }
      } catch (err) {
        console.error('Error running eligibility check:', err);
      } finally {
        this.isAssessing = false;
      }
    },

    // Fetch All Jobs Catalog
    async fetchCatalog() {
      this.isLoadingCatalog = true;
      try {
        const params = new URLSearchParams();
        if (this.searchQuery) params.append('search', this.searchQuery);
        if (this.selectedTier) params.append('tier', this.selectedTier);
        if (this.selectedSector) params.append('sector', this.selectedSector);
        if (this.selectedStatus) params.append('status', this.selectedStatus);
        if (this.selectedEdu) params.append('education', this.selectedEdu);
        if (this.sortBy) params.append('sort', this.sortBy);

        const res = await fetch(`/api/jobs?${params.toString()}`);
        const data = await res.json();
        if (data.success) {
          this.catalogJobs = data.jobs;
        }
      } catch (err) {
        console.error('Error fetching catalog:', err);
      } finally {
        this.isLoadingCatalog = false;
      }
    },

    // Fetch Deadlines
    async fetchDeadlines() {
      this.isLoadingDeadlines = true;
      try {
        const res = await fetch('/api/deadlines');
        const data = await res.json();
        if (data.success) {
          this.deadlines = data.deadlines;
        }
      } catch (err) {
        console.error('Error fetching deadlines:', err);
      } finally {
        this.isLoadingDeadlines = false;
      }
    },

    get filteredDeadlines() {
      if (this.deadlineFilter === 'all') return this.deadlines;
      return this.deadlines.filter(d => d.status === this.deadlineFilter);
    },

    get bookmarkedJobs() {
      return this.catalogJobs.filter(j => this.bookmarkedIds.includes(j.id));
    },

    // Bookmark Toggle
    toggleBookmark(jobId) {
      if (this.bookmarkedIds.includes(jobId)) {
        this.bookmarkedIds = this.bookmarkedIds.filter(id => id !== jobId);
      } else {
        this.bookmarkedIds.push(jobId);
      }
      localStorage.setItem('govjob_bookmarks', JSON.stringify(this.bookmarkedIds));
    },

    isBookmarked(jobId) {
      return this.bookmarkedIds.includes(jobId);
    },

    // Modal Control
    openJobDetail(job) {
      this.activeJobModal = job;
    },

    closeJobModal() {
      this.activeJobModal = null;
    },

    // AI Counselor Query
    async askAi(promptText) {
      const q = promptText || this.aiQuery;
      if (!q.trim()) return;

      this.chatHistory.push({
        sender: 'user',
        text: q
      });
      this.aiQuery = '';
      this.isAiTyping = true;

      try {
        const res = await fetch('/api/ai-counselor', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            query: q,
            profile: this.profile
          })
        });
        const data = await res.json();
        if (data.success && data.guidance) {
          this.chatHistory.push({
            sender: 'ai',
            title: data.guidance.title,
            text: data.guidance.response,
            actions: data.guidance.suggested_actions
          });
        }
      } catch (e) {
        this.chatHistory.push({
          sender: 'ai',
          title: 'Guidance Unavailable',
          text: 'Sorry, unable to connect to the advisor right now. Please try again.'
        });
      } finally {
        this.isAiTyping = false;
      }
    },

    // Alert Subscription
    async submitAlert() {
      if (!this.alertContact) return;
      try {
        const res = await fetch('/api/subscribe-alert', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            contact: this.alertContact,
            category: this.profile.category,
            education: this.profile.education_level
          })
        });
        const data = await res.json();
        if (data.success) {
          this.alertSubmitted = true;
          this.alertMsg = data.message;
          setTimeout(() => {
            this.showAlertModal = false;
            this.alertSubmitted = false;
            this.alertContact = '';
          }, 2500);
        }
      } catch (e) {
        alert('Failed to register subscription.');
      }
    },

    // Calendar Link Generator
    getGoogleCalendarUrl(job) {
      const title = encodeURIComponent(`Application Deadline: ${job.title || job.job_title}`);
      const details = encodeURIComponent(`Apply before deadline on ${job.app_end_date}. Official Portal: ${job.apply_url}`);
      // Format date YYYYMMDD
      const rawDate = (job.app_end_date || '2026-10-01').replace(/-/g, '');
      const dates = `${rawDate}T090000Z/${rawDate}T180000Z`;
      return `https://calendar.google.com/calendar/render?action=TEMPLATE&text=${title}&dates=${dates}&details=${details}`;
    },

    // Print Report
    printReport() {
      window.print();
    }
  }));
});
