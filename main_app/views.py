from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic.edit import CreateView
from django.contrib.auth import login
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import JobTitle, JobPost
from .forms import JobPostForm, JobPostUpdateForm


def home(request):
    jobTitle = JobTitle.objects.all()
    return render(request, 'home.html', {
        'jobTitle': jobTitle
    })


def search(request):
    results = []
    # creating an array
    if request.method == "GET":
        query = request.GET.get('search')
        if query == '':
            query = 'None'
        results = JobTitle.objects.filter(job_title__contains=query)
        # updating results with our filtered data
    return render(request, 'home.html', {'jobTitle': results})

# wrote view function because we needed to associate
# both the user and the JobTitle with the job post being created


@login_required
def JobPostCreate(request, job_title_id):
    title = JobTitle.objects.filter(pk=job_title_id)
    job_form = JobPostForm(request.POST)

    if job_form.is_valid():
        new_job_post = job_form.save(commit=False)
        new_job_post.user_id = request.user.id
        # save every time new_job_post gets manipulated
        new_job_post.save()
        new_job_post.job_title.set(title)
        new_job_post.save()
        # return to detail of selected Job Title
        # ('detail' path in urls.py)
        # this first job_title_id is taking the parameter
        # and reassigning it
        # (re-passing the parameter so we can use it on the page)
    return redirect('detail', job_title_id=job_title_id)


@login_required
def GetJobPostForm(request, job_title_id):
    # assigning the JobTitle we made the request from
    # to this variable
    jobtitle = JobTitle.objects.get(pk=job_title_id)
    # render the form (jobpost_form.html)
    jobform = JobPostForm()
    return render(request, 'main_app/jobpost_form.html', {
        'JobTitle': jobtitle,
        'JobForm': jobform
    })


@login_required
def GetJobPostUpdate(request, job_post_id):
    # get request for form
    # find post from primary key
    job_post = JobPost.objects.get(pk=job_post_id)
    # which form model we are using
    jobupdateform = JobPostUpdateForm()
    # what page to go to
    return render(request, 'main_app/jobpost_update.html', {
        # passing the job post & form to the page listed above
        'JobPost': job_post,
        'JobUpdateForm': jobupdateform
    })


@login_required
def UpdateJobPost(request, job_post_id):
    # get_object_or_404 = .get with error handling
    job_post = get_object_or_404(JobPost, pk=job_post_id)
    # request.POST or None = post or throw error
    job_form = JobPostUpdateForm(request.POST or None, instance=job_post)
    if job_form.is_valid():
        # defines the form but wait to save
        updated_job = job_form.save(commit=False)
        # add the userid
        updated_job.user_id = request.user.id
        # this save updates the database
        updated_job.save()
    return redirect('home')


class JobTitleCreate(LoginRequiredMixin, CreateView):
    model = JobTitle
    fields = '__all__'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)


def job_post_delete(request, job_post_id):
    JobPost.objects.filter(id=job_post_id).delete()
    return redirect('home')


def signup(request):
    error_message = ''
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
        else:
            error_message = 'Invalid signup - try again!'
    form = UserCreationForm()
    context = {'form': form, 'error_message': error_message}
    return render(request, 'registration/signup.html', context)


def job_title_detail(request, job_title_id):
    details = JobPost.objects.filter(job_title=job_title_id)
    # allows us to access the jobTitle name for the detail page
    job_title = JobTitle.objects.get(id=job_title_id)
    return render(request, 'everyJobs/detail.html', {
        'jobPost': details,
        'job_title': job_title
    })
