(function () {
    
    function getParentByTagName(el, tagName) {
        var p = el.parentElement;

        if (p.tagName === tagName.toUpperCase()) {
            return p;
        } else {
            return getParentByTagName(p, tagName);
        }
    }

    var uploads = 0;
    function disableSubmit(el, status) {
        if (status) uploads++;
        else uploads--;

        var form = getParentByTagName(el, 'form');
        var submitBtn = form.querySelector('[type="submit"');

        submitBtn.disabled = (uploads > 0);
    }

    function error(el, msg) {
        el.querySelector('.file-url').value = '';
        el.querySelector('.file-input').value = '';

        if (errs = el.querySelector('.errors')) { errs.remove(); }

        var errorList = document.createElement('ul');
        errorList.setAttribute('class', 'errors');
        var errorMessage = document.createElement('li');
        errorMessage.appendChild(document.createTextNode(msg))
        errorList.appendChild(errorMessage);

        el.insertBefore(errorList, el.firstChild);
    }

    function getUrl(text) {
        var xml = new DOMParser().parseFromString(text, 'text/xml'),
            tag = xml.getElementsByTagName('Location')[0],
            url = unescape(tag.childNodes[0].nodeValue)

        return url
    }

    function update(el, xml) {
        var link = el.querySelector('.file-link'),
            url = el.querySelector('.file-url');

        if (errs = el.querySelector('.errors')) { errs.remove(); }

        url.value = getUrl(xml);
        link.href = url.value;
        link.innerHTML = url.value.split('/').pop();

        el.classList.add('uploaded');
    }

    function getCookie(name) {
        var value = '; ' + document.cookie,
            parts = value.split('; ' + name + '=')
        if (parts.length == 2) return parts.pop().split(';').shift()
    }

    function request(method, url, data, headers, el, callback) {
        var req = new XMLHttpRequest();
        req.open(method, url, true);

        Object.keys(headers).forEach(function(key){
            req.setRequestHeader(key, headers[key])
        });

        req.onload = function() {
            disableSubmit(el, false)
            callback(req.status, req.responseText);
        }

        req.onerror = req.onabort = function() {
            disableSubmit(el, false)
            error(el, 'Not able to upload file');
        }

        req.send(data)
    }

    function uploadFile(e) {

        var el = e.target.parentElement,
            file = el.querySelector('.file-input').files[0],
            url = el.getAttribute('data-upload-url'),
            form = new FormData(),
            headers  = {'X-CSRFToken': getCookie('csrftoken')};

        disableSubmit(el, true);
        form.append('file', file);
        
        request('POST', url, form, headers, el, function(status, xml) {
            if (status !== 201) {
                error(el, 'Not able to upload file')
            } else {
                update(el, xml);
            }
        });
    }

    function removeFile(e) {
        e.preventDefault();

        var el = e.target.parentElement.parentElement;
        el.querySelector('.file-url').value = '';
        el.querySelector('.file-input').value = '';
        el.classList.remove('uploaded');
    }

    function addEventHandlers(el) {
        var input = el.querySelector('.file-input'),
            remove = el.querySelector('.file-remove');

        input.addEventListener('change', uploadFile, false);
        remove.addEventListener('click', removeFile, false);
    }

    document.addEventListener('DOMContentLoaded', function(e) {
        ;[].forEach.call(document.querySelectorAll('.s3-buckets'), addEventHandlers)
    })

    document.addEventListener('DOMNodeInserted', function(e){
        if(e.target.tagName) {
            var el = e.target.querySelector('.s3-buckets')
            if(el) addEventHandlers(el)
        }
    })
}());
